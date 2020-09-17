from __future__ import annotations

import datetime
import inspect
import os
from functools import partial, update_wrapper
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Type, TypeVar, Union, overload
from typing import Literal as L

from typing_extensions import ParamSpec  # type: ignore

from flytekit.core import launch_plan as _annotated_launchplan
from flytekit.core import workflow as _annotated_workflow
from flytekit.core.base_task import PythonTask, TaskMetadata, TaskResolverMixin
from flytekit.core.cache import Cache, VersionParameters
from flytekit.core.interface import Interface, output_name_generator, transform_function_to_interface
from flytekit.core.pod_template import PodTemplate
from flytekit.core.python_function_task import AsyncPythonFunctionTask, EagerAsyncPythonFunctionTask, PythonFunctionTask
from flytekit.core.reference_entity import ReferenceEntity, TaskReference
from flytekit.core.resources import Resources
from flytekit.core.utils import str2bool
from flytekit.deck import DeckField
from flytekit.extras.accelerators import BaseAccelerator
from flytekit.image_spec.image_spec import ImageSpec
from flytekit.interactive import vscode
from flytekit.interactive.constants import FLYTE_ENABLE_VSCODE_KEY
from flytekit.models.documentation import Documentation
from flytekit.models.security import Secret


class TaskPlugins(object):
    """
    This is the TaskPlugins factory for task types that are derivative of PythonFunctionTask.
    Every task that the user wishes to use should be available in this factory.
    Usage

    ```python
    TaskPlugins.register_pythontask_plugin(config_object_type, plugin_object_type)
    # config_object_type is any class that will be passed to the plugin_object as task_config
    # Plugin_object_type is a derivative of ``PythonFunctionTask``
    ```
    Examples of available task plugins include different query-based plugins such as
    {{< py_class_ref flytekitplugins.athena.task.AthenaTask >}} and {{< py_class_ref flytekitplugins.hive.task.HiveTask >}}, kubeflow
    operators like {{< py_class_ref plugins.kfpytorch.flytekitplugins.kfpytorch.task.PyTorchFunctionTask >}} and
    {{< py_class_ref plugins.kftensorflow.flytekitplugins.kftensorflow.task.TensorflowFunctionTask >}}, and generic plugins like
    {{< py_class_ref flytekitplugins.pod.task.PodFunctionTask >}} which doesn't integrate with third party tools or services.

    The `task_config` is different for every task plugin type. This is filled out by users when they define a task to
    specify plugin-specific behavior and features.  For example, with a query type task plugin, the config might store
    information related to which database to query.

    The `plugin_object_type` can be used to customize execution behavior and task serialization properties in tandem
    with the `task_config`.
    """

    _PYTHONFUNCTION_TASK_PLUGINS: Dict[type, Type[PythonFunctionTask]] = {}

    @classmethod
    def register_pythontask_plugin(cls, plugin_config_type: type, plugin: Type[PythonFunctionTask]):
        """
        Use this method to register a new plugin into Flytekit. Usage ::

        ```python
        TaskPlugins.register_pythontask_plugin(config_object_type, plugin_object_type)
        # config_object_type is any class that will be passed to the plugin_object as task_config
        # Plugin_object_type is a derivative of ``PythonFunctionTask``
        ```
        """
        if plugin_config_type in cls._PYTHONFUNCTION_TASK_PLUGINS:
            found = cls._PYTHONFUNCTION_TASK_PLUGINS[plugin_config_type]
            if found == plugin:
                return
            raise TypeError(
                f"Requesting to register plugin {plugin} - collides with existing plugin {found}"
                f" for type {plugin_config_type}"
            )

        cls._PYTHONFUNCTION_TASK_PLUGINS[plugin_config_type] = plugin

    @classmethod
    def find_pythontask_plugin(cls, plugin_config_type: type) -> Type[PythonFunctionTask]:
        """
        Returns a PluginObjectType if found or returns the base PythonFunctionTask
        """
        if plugin_config_type in cls._PYTHONFUNCTION_TASK_PLUGINS:
            return cls._PYTHONFUNCTION_TASK_PLUGINS[plugin_config_type]
        # Defaults to returning Base PythonFunctionTask
        return PythonFunctionTask


P = ParamSpec("P")
T = TypeVar("T")
FuncOut = TypeVar("FuncOut")


@overload
def task(
    _task_function: None = ...,
    task_config: Optional[T] = ...,
    cache: Union[bool, Cache] = ...,
    retries: int = ...,
    interruptible: Optional[bool] = ...,
    deprecated: str = ...,
    timeout: Union[datetime.timedelta, int] = ...,
    container_image: Optional[Union[str, ImageSpec]] = ...,
    environment: Optional[Dict[str, str]] = ...,
    requests: Optional[Resources] = ...,
    limits: Optional[Resources] = ...,
    secret_requests: Optional[List[Secret]] = ...,
    execution_mode: PythonFunctionTask.ExecutionBehavior = ...,
    node_dependency_hints: Optional[
        Iterable[
            Union[
                PythonFunctionTask,
                _annotated_launchplan.LaunchPlan,
                _annotated_workflow.WorkflowBase,
            ]
        ]
    ] = ...,
    task_resolver: Optional[TaskResolverMixin] = ...,
    docs: Optional[Documentation] = ...,
