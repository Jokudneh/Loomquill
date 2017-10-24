"""
This Plugin adds the capability of running distributed MPI training to Flyte using backend plugins, natively on
Kubernetes. It leverages [`MPI Job`](https://github.com/kubeflow/mpi-operator) Plugin from kubeflow.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from flyteidl.plugins.kubeflow import common_pb2 as kubeflow_common
from flyteidl.plugins.kubeflow import mpi_pb2 as mpi_task
from google.protobuf.json_format import MessageToDict

from flytekit import PythonFunctionTask, Resources
from flytekit.configuration import SerializationSettings
from flytekit.core.resources import convert_resources_to_resource_model
from flytekit.extend import TaskPlugins


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
        clean_pod_policy: Defines the policy for cleaning up pods after the PyTorchJob completes. Default to None.
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
    """
