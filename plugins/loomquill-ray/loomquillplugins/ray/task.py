import base64
import json
import os
import typing
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

import yaml
from flytekitplugins.ray.models import (
    AutoscalerOptions,
    HeadGroupSpec,
    RayCluster,
    RayJob,
    WorkerGroupSpec,
)
from google.protobuf.json_format import MessageToDict

from flytekit import PodTemplate, Resources, lazy_module
from flytekit.configuration import SerializationSettings
from flytekit.core.context_manager import ExecutionParameters, FlyteContextManager
from flytekit.core.python_function_task import PythonFunctionTask
from flytekit.core.resources import convert_resources_to_resource_model, pod_spec_from_resources
from flytekit.extend import TaskPlugins
from flytekit.models.task import K8sPod

ray = lazy_module("ray")
_RAY_HEAD_CONTAINER_NAME = "ray-head"
_RAY_WORKER_CONTAINER_NAME = "ray-worker"


@dataclass
class HeadNodeConfig:
    ray_start_params: typing.Optional[typing.Dict[str, str]] = None
    pod_template: typing.Optional[PodTemplate] = None
    requests: Optional[Resources] = None
    limits: Optional[Resources] = None

    def __post_init__(self):
        if self.pod_template:
            if self.requests and self.limits:
                raise ValueError("Cannot specify both pod_template and requests/limits")


@dataclass
class WorkerNodeConfig:
    group_name: str
    replicas: int
    min_replicas: typing.Optional[int] = None
    max_replicas: typing.Optional[int] = None
    ray_start_params: typing.Optional[typing.Dict[str, str]] = None
    pod_template: typing.Optional[PodTemplate] = None
    requests: Optional[Resources] = None
