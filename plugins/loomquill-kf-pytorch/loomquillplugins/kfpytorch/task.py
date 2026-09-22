"""
This Plugin adds the capability of running distributed pytorch training to Flyte using backend plugins, natively on
Kubernetes. It leverages [`Pytorch Job`](https://github.com/kubeflow/pytorch-operator) Plugin from kubeflow.
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Union

from flyteidl.plugins.kubeflow import common_pb2 as kubeflow_common
from flyteidl.plugins.kubeflow import pytorch_pb2 as pytorch_task
from google.protobuf.json_format import MessageToDict

import flytekit
from flytekit import PythonFunctionTask, Resources, lazy_module
from flytekit.configuration import SerializationSettings
from flytekit.core.context_manager import FlyteContextManager, OutputMetadata
from flytekit.core.pod_template import PodTemplate
from flytekit.core.resources import convert_resources_to_resource_model
from flytekit.exceptions.user import FlyteRecoverableException, FlyteUserRuntimeException
from flytekit.extend import IgnoreOutputs, TaskPlugins
from flytekit.loggers import logger

from .error_handling import create_recoverable_error_file, is_recoverable_worker_error
from .pod_template import add_shared_mem_volume_to_pod_template

cloudpickle = lazy_module("cloudpickle")

TORCH_IMPORT_ERROR_MESSAGE = "PyTorch is not installed. Please install `flytekitplugins-kfpytorch['elastic']`."


@dataclass
class RestartPolicy(Enum):
    """
    RestartPolicy describes how the replicas should be restarted
    """

    ALWAYS = kubeflow_common.RESTART_POLICY_ALWAYS
    FAILURE = kubeflow_common.RESTART_POLICY_ON_FAILURE
    NEVER = kubeflow_common.RESTART_POLICY_NEVER


@dataclass
class CleanPodPolicy(Enum):
    """
    CleanPodPolicy describes how to deal with pods when the job is finished.
    """

    NONE = kubeflow_common.CLEANPOD_POLICY_NONE
    ALL = kubeflow_common.CLEANPOD_POLICY_ALL
    RUNNING = kubeflow_common.CLEANPOD_POLICY_RUNNING


@dataclass
class RunPolicy:
    """
    RunPolicy describes some policy to apply to the execution of a kubeflow job.
    Args:
        clean_pod_policy (int): Defines the policy for cleaning up pods after the PyTorchJob completes. Default to None.
        ttl_seconds_after_finished (int): Defines the TTL for cleaning up finished PyTorchJobs.
        active_deadline_seconds (int): Specifies the duration (in seconds) since startTime during which the job.
        can remain active before it is terminated. Must be a positive integer. This setting applies only to pods.
        where restartPolicy is OnFailure or Always.
        backoff_limit (int): Number of retries before marking this job as failed.
    """

    clean_pod_policy: CleanPodPolicy = None
    ttl_seconds_after_finished: Optional[int] = None
    active_deadline_seconds: Optional[int] = None
    backoff_limit: Optional[int] = None


@dataclass
class Worker:
    image: Optional[str] = None
    requests: Optional[Resources] = None
    limits: Optional[Resources] = None
    replicas: Optional[int] = None
    restart_policy: Optional[RestartPolicy] = None


@dataclass
class Master:
    """
    Configuration for master replica group. Master should always have 1 replica, so we don't need a `replicas` field
    """

    image: Optional[str] = None
    requests: Optional[Resources] = None
    limits: Optional[Resources] = None
    restart_policy: Optional[RestartPolicy] = None


@dataclass
class PyTorch(object):
    """
    Configuration for an executable [`PyTorch Job`](https://github.com/kubeflow/pytorch-operator). Use this
    to run distributed PyTorch training on Kubernetes. Please notice, in most cases, you should not worry
    about the configuration of the master and worker groups. The default configuration should work. The only
    field you should change is the number of workers. Both replicas will use the same image, and the same
    resources inherited from task function decoration.

    Args:
        master: Configuration for the master replica group.
        worker: Configuration for the worker replica group.
        run_policy: Configuration for the run policy.
        num_workers: [DEPRECATED] This argument is deprecated. Use `worker.replicas` instead.
        increase_shared_mem (bool): [DEPRECATED] This argument is deprecated. Use `@task(shared_memory=...)` instead.
            PyTorch uses shared memory to share data between processes. If torch multiprocessing is used
            (e.g. for multi-processed data loaders) the default shared memory segment size that the container runs with might not be enough
            and and one might have to increase the shared memory size. This option configures the task's pod template to mount
            an `emptyDir` volume with medium `Memory` to to `/dev/shm`.
            The shared memory size upper limit is the sum of the memory limits of the containers in the pod.
    """

    master: Master = field(default_factory=lambda: Master())
    worker: Worker = field(default_factory=lambda: Worker())
    run_policy: Optional[RunPolicy] = None
    # Support v0 config for backwards compatibility
    num_workers: Optional[int] = None
    increase_shared_mem: bool = True


@dataclass
class Elastic(object):
    """
    Configuration for [`torch elastic training`](https://pytorch.org/docs/stable/elastic/run.html).

    Use this to run single- or multi-node distributed pytorch elastic training on k8s.

    Single-node elastic training is executed in a k8s pod when `nnodes` is set to 1.
    Multi-node training is executed otherwise using a [`Pytorch Job`](https://github.com/kubeflow/training-operator).

    Like `torchrun`, this plugin sets the environment variable `OMP_NUM_THREADS` to 1 if it is not set.
    Please see https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html for potential performance improvements.
    To change `OMP_NUM_THREADS`, specify it in the environment dict of the flytekit task decorator or via `pyflyte run --env`.

    Args:
        nnodes (Union[int, str]): Number of nodes, or the range of nodes in form <minimum_nodes>:<maximum_nodes>.
        nproc_per_node (str): Number of workers per node.
        start_method (str): Multiprocessing start method to use when creating workers.
        monitor_interval (int): Interval, in seconds, to monitor the state of workers.
        max_restarts (int): Maximum number of worker group restarts before failing.
        rdzv_configs (Dict[str, Any]): Additional rendezvous configs to pass to torch elastic, e.g., `{"timeout": 1200, "join_timeout": 900}`.
            See `torch.distributed.launcher.api.LaunchConfig` and `torch.distributed.elastic.rendezvous.dynamic_rendezvous.create_handler`.
            Default timeouts are set to 15 minutes to account for the fact that some workers might start faster than others: Some pods might
            be assigned to a running node which might have the image in its cache while other workers might require a node scale up and image pull.
            When using the default `torch.distributed.elastic.rendezvous.c10d_rendezvous_backend.C10dRendezvousBackend`, consider also increasing
            the TCPStore `read_timeout`, e.g., {"timeout": 900, "join_timeout": 900, "read_timeout": 900}, as its default value of 60 seconds
            might be too tight if the zero-worker starts slower than any other worker.
            Increasing the default timeouts is mostly relevant in the absence of true gang-scheduling on the cluster, as provided by e.g.
            coscheduling or volcano.

        increase_shared_mem (bool): [DEPRECATED] This argument is deprecated. Use `@task(shared_memory=...)` instead.
            PyTorch uses shared memory to share data between processes. If torch multiprocessing is used
            (e.g. for multi-processed data loaders) the default shared memory segment size that the container runs with might not be enough
            and one might have to increase the shared memory size. This option configures the task's pod template to mount
            an `emptyDir` volume with medium `Memory` to to `/dev/shm`.
            The shared memory size upper limit is the sum of the memory limits of the containers in the pod.
        run_policy: Configuration for the run policy.
    """

    nnodes: Union[int, str] = 1
    nproc_per_node: int = 1
    start_method: str = "spawn"
    monitor_interval: int = 5
    max_restarts: int = 0
    rdzv_configs: Dict[str, Any] = field(default_factory=lambda: {"timeout": 900, "join_timeout": 900})
    increase_shared_mem: bool = True
    run_policy: Optional[RunPolicy] = None
