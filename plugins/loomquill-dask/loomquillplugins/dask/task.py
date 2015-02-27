from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from flytekitplugins.dask import models
from google.protobuf.json_format import MessageToDict

from flytekit import PythonFunctionTask, Resources
from flytekit.configuration import SerializationSettings
from flytekit.core.resources import convert_resources_to_resource_model
from flytekit.core.task import TaskPlugins


@dataclass
class Scheduler:
    """
    Configuration for the scheduler pod

    :param image: Custom image to use. If ``None``, will use the same image the task was registered with. Optional,
        defaults to ``None``. The image must have ``dask[distributed]`` installed and should have the same Python
        environment as the rest of the cluster (job runner pod + worker pods).
    :param requests: Resources to request for the scheduler pod. If ``None``, the requests passed into the task will be
        used. Optional, defaults to ``None``.
    :param limits: Resource limits for the scheduler pod. If ``None``, the limits passed into the task will be used.
        Optional, defaults to ``None``.
    """

    image: Optional[str] = None
    requests: Optional[Resources] = None
    limits: Optional[Resources] = None
