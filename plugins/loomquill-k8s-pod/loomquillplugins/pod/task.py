from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple, Union

from flyteidl.core import tasks_pb2 as _core_task

from flytekit import FlyteContext, PythonFunctionTask, lazy_module
from flytekit.configuration import SerializationSettings
from flytekit.exceptions import user as _user_exceptions
from flytekit.extend import Promise, TaskPlugins
from flytekit.loggers import logger
from flytekit.models import task as _task_models

_PRIMARY_CONTAINER_NAME_FIELD = "primary_container_name"
PRIMARY_CONTAINER_DEFAULT_NAME = "primary"


k8s_client = lazy_module("kubernetes.client")
k8s_models = lazy_module("kubernetes.client.models")


def _sanitize_resource_name(resource: _task_models.Resources.ResourceEntry) -> str:
    return _core_task.Resources.ResourceName.Name(resource.name).lower().replace("_", "-")


@dataclass
class Pod(object):
    """
    Pod is a platform-wide configuration that uses pod templates. By default, every task is launched as a container in a pod.
    This plugin helps expose a fully modifiable Kubernetes pod spec to customize the task execution runtime.
    To use pod tasks: (1) Define a pod spec, and (2) Specify the primary container name.

    :param V1PodSpec pod_spec: Kubernetes pod spec. https://kubernetes.io/docs/concepts/workloads/pods
    :param str primary_container_name: the primary container name. If provided the pod-spec can contain a container whose name matches the primary_container_name. This will force Flyte to give up control of the primary
        container and will expect users to control setting up the container. If you expect your python function to run as is, simply create containers that do not match the default primary-container-name and Flyte will auto-inject a
        container for the python function based on the default image provided during serialization.
    :param Optional[Dict[str, str]] labels: Labels are key/value pairs that are attached to pod spec
    :param Optional[Dict[str, str]] annotations: Annotations are key/value pairs that are attached to arbitrary non-identifying metadata to pod spec.
    """

