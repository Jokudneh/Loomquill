from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Type, TypeVar

from flyteidl.core import tasks_pb2 as _tasks_pb2

from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.core.base_task import PythonTask, Task, TaskResolverMixin
from flytekit.core.context_manager import FlyteContext
from flytekit.core.python_auto_container import get_registerable_container_image
from flytekit.core.resources import Resources, ResourceSpec
from flytekit.core.shim_task import ExecutableTemplateShimTask, ShimTaskExecutor
from flytekit.core.tracker import TrackedInstance
from flytekit.core.utils import _get_container_definition, load_proto_from_file
from flytekit.image_spec.image_spec import ImageSpec
from flytekit.loggers import logger
from flytekit.models import task as _task_model
from flytekit.models.core import identifier as identifier_models
from flytekit.models.security import Secret, SecurityContext
from flytekit.tools.module_loader import load_object_from_module

TC = TypeVar("TC")


class PythonCustomizedContainerTask(ExecutableTemplateShimTask, PythonTask[TC]):  # type: ignore
    """
    Please take a look at the comments for {{< py_class_ref flytekit.extend.ExecutableTemplateShimTask >}} as well. This class
    should be subclassed and a custom Executor provided as a default to this parent class constructor
    when building a new external-container flytekit-only plugin.

    This class provides authors of new task types the basic scaffolding to create task-template based tasks. In order
    to write such a task, authors need to

    * subclass the ``ShimTaskExecutor`` class  and override the ``execute_from_model`` function. This function is
      where all the business logic should go. Keep in mind though that you, the plugin author, will not have access
      to anything that's not serialized within the ``TaskTemplate`` which is why you'll also need to
    * subclass this class, and override the ``get_custom`` function to include all the information the executor
      will need to run.
    * Also pass the executor you created as the ``executor_type`` argument of this class's constructor.

    Keep in mind that the total size of the ``TaskTemplate`` still needs to be small, since these will be accessed
    frequently by the Flyte engine.
    """

    SERIALIZE_SETTINGS = SerializationSettings(
        project="PLACEHOLDER_PROJECT",
        domain="LOCAL",
        version="PLACEHOLDER_VERSION",
        env=None,
        image_config=ImageConfig(
            default_image=Image(name="custom_container_task", fqn="flyteorg.io/placeholder", tag="image")
        ),
    )

    def __init__(
        self,
        name: str,
        task_config: TC,
        container_image: str,
        executor_type: Type[ShimTaskExecutor],
        task_resolver: Optional[TaskTemplateResolver] = None,
        task_type="python-task",
        requests: Optional[Resources] = None,
        limits: Optional[Resources] = None,
        environment: Optional[Dict[str, str]] = None,
        secret_requests: Optional[List[Secret]] = None,
        **kwargs,
    ):
        """
        :param name: unique name for the task, usually the function's module and name.
        :param task_config: Configuration object for Task. Should be a unique type for that specific Task
        :param container_image: This is the external container image the task should run at platform-run-time.
