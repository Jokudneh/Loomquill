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
