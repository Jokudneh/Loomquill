from __future__ import annotations

import inspect
import os
import signal
import time
import typing
from abc import ABC
from collections import OrderedDict
from contextlib import suppress
from enum import Enum
from typing import Any, Callable, Iterable, List, Optional, Tuple, TypeVar, Union, cast

from flytekit.configuration import ImageConfig, ImageSpec, SerializationSettings
from flytekit.core import launch_plan as _annotated_launch_plan
from flytekit.core.base_task import Task, TaskMetadata, TaskResolverMixin
from flytekit.core.constants import EAGER_ROOT_ENV_NAME
from flytekit.core.context_manager import ExecutionState, FlyteContext, FlyteContextManager
from flytekit.core.docstring import Docstring
from flytekit.core.interface import Interface, transform_function_to_interface
from flytekit.core.promise import (
    Promise,
    VoidPromise,
    async_flyte_entity_call_handler,
    translate_inputs_to_literals,
)
from flytekit.core.python_auto_container import (
    PythonAutoContainerTask,
    default_task_resolver,
)
from flytekit.core.tracked_abc import FlyteTrackedABC
from flytekit.core.tracker import extract_task_module, is_functools_wrapped_module_level, isnested, istestfunction
from flytekit.core.utils import _dnsify
from flytekit.core.worker_queue import Controller
from flytekit.core.workflow import (
    PythonFunctionWorkflow,
    WorkflowBase,
    WorkflowFailurePolicy,
    WorkflowMetadata,
    WorkflowMetadataDefaults,
)
from flytekit.deck.deck import Deck
from flytekit.exceptions.eager import EagerException
from flytekit.exceptions.system import FlyteNonRecoverableSystemException
from flytekit.exceptions.user import FlyteValueException
from flytekit.loggers import logger
from flytekit.models import dynamic_job as _dynamic_job
from flytekit.models import literals as _literal_models
from flytekit.models import task as task_models
from flytekit.models.admin import common as admin_common_models
from flytekit.models.admin import workflow as admin_workflow_models
from flytekit.models.filters import ValueIn
from flytekit.models.literals import LiteralMap
from flytekit.utils.asyn import loop_manager

T = TypeVar("T")

CLEANUP_LOOP_DELAY_SECONDS = 1


class PythonInstanceTask(PythonAutoContainerTask[T], ABC):  # type: ignore
    """
    This class should be used as the base class for all Tasks that do not have a user defined function body, but have
    a platform defined execute method. (Execute needs to be overridden). This base class ensures that the module loader
    will invoke the right class automatically, by capturing the module name and variable in the module name.

    ```python
    x = MyInstanceTask(name="x", .....)

    # this can be invoked as
    x(a=5) # depending on the interface of the defined task
    ```

    """

    def __init__(
        self,
        name: str,
        task_config: T,
        task_type: str = "python-task",
        task_resolver: Optional[TaskResolverMixin] = None,
        **kwargs,
    ):
        """
        Please see class level documentation.
        """
        super().__init__(name=name, task_config=task_config, task_type=task_type, task_resolver=task_resolver, **kwargs)


class PythonFunctionTask(PythonAutoContainerTask[T]):  # type: ignore
    """
    A Python Function task should be used as the base for all extensions that have a python function. It will
    automatically detect interface of the python function and when serialized on the hosted Flyte platform handles the
    writing execution command to execute the function

    It is advised this task is used using the @task decorator as follows

    ```python
    @task
    def my_func(a: int) -> str:
        ...
    ```
    In the above code, the name of the function, the module, and the interface (inputs = int and outputs = str) will be
    auto detected.
    """

    class ExecutionBehavior(Enum):
        DEFAULT = 1
        DYNAMIC = 2
        EAGER = 3

    def __init__(
        self,
        task_config: T,
        task_function: Callable,
        task_type="python-task",
        ignore_input_vars: Optional[List[str]] = None,
        execution_mode: ExecutionBehavior = ExecutionBehavior.DEFAULT,
        task_resolver: Optional[TaskResolverMixin] = None,
        node_dependency_hints: Optional[
            Iterable[Union["PythonFunctionTask", "_annotated_launch_plan.LaunchPlan", WorkflowBase]]
        ] = None,
        pickle_untyped: bool = False,
        **kwargs,
    ):
        """
        :param T task_config: Configuration object for Task. Should be a unique type for that specific Task
        :param Callable task_function: Python function that has type annotations and works for the task
        :param Optional[List[str]] ignore_input_vars: When supplied, these input variables will be removed from the
        interface. This
                                  can be used to inject some client side variables only. Prefer using ExecutionParams
        :param Optional[ExecutionBehavior] execution_mode: Defines how the execution should behave, for example
            executing normally or specially handling a dynamic case.
        :param str task_type: String task type to be associated with this Task
        :param Optional[Iterable[Union["PythonFunctionTask", "_annotated_launch_plan.LaunchPlan", WorkflowBase]]]
        node_dependency_hints:
            A list of tasks, launchplans, or workflows that this task depends on. This is only
            for dynamic tasks/workflows, where flyte cannot automatically determine the dependencies prior to runtime.
        :param bool pickle_untyped: If set to True, the task will pickle untyped outputs. This is just a convenience
            flag to avoid having to specify the output types in the interface. This is not recommended for production
            use.
        """
        if task_function is None:
            raise ValueError("TaskFunction is a required parameter for PythonFunctionTask")
        self._native_interface = transform_function_to_interface(
            task_function, Docstring(callable_=task_function), pickle_untyped=pickle_untyped
        )
        mutated_interface = self._native_interface.remove_inputs(ignore_input_vars)
        name, _, _, _ = extract_task_module(task_function)
        super().__init__(
            task_type=task_type,
            name=name,
            interface=mutated_interface,
            task_config=task_config,
            task_resolver=task_resolver,
            **kwargs,
