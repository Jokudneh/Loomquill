# TODO: has to support the SupportsNodeCreation protocol
import functools
import hashlib
import math
import os  # TODO: use flytekit logger
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Union, cast

from flyteidl.core import tasks_pb2
from flyteidl.core import workflow_pb2 as _core_workflow

from flytekit.configuration import SerializationSettings
from flytekit.core import tracker
from flytekit.core.array_node import array_node
from flytekit.core.base_task import PythonTask, TaskResolverMixin
from flytekit.core.context_manager import ExecutionState, FlyteContext, FlyteContextManager
from flytekit.core.interface import transform_interface_to_list_interface
from flytekit.core.launch_plan import LaunchPlan
from flytekit.core.python_function_task import PythonFunctionTask, PythonInstanceTask
from flytekit.core.task import ReferenceTask
from flytekit.core.type_engine import TypeEngine
from flytekit.core.utils import timeit
from flytekit.loggers import logger
from flytekit.models import literals as _literal_models
from flytekit.models.core.workflow import NodeMetadata
from flytekit.models.interface import Variable
from flytekit.models.task import Container, K8sPod, Sql, Task
from flytekit.tools.module_loader import load_object_from_module
from flytekit.utils.asyn import loop_manager

if TYPE_CHECKING:
    from flytekit.remote import FlyteLaunchPlan


class ArrayNodeMapTask(PythonTask):
    def __init__(
        self,
        # TODO: add support for other Flyte entities
        python_function_task: Union[PythonFunctionTask, PythonInstanceTask, functools.partial],
        concurrency: Optional[int] = None,
        min_successes: Optional[int] = None,
        min_success_ratio: Optional[float] = None,
        bound_inputs: Optional[Set[str]] = None,
        bound_inputs_values: Optional[Dict[str, Any]] = None,
        run_all_sub_nodes: bool = False,
        **kwargs,
    ):
        """
        :param python_function_task: The task to be executed in parallel
        :param concurrency: The number of parallel executions to run
        :param min_successes: The minimum number of successful executions
        :param min_success_ratio: The minimum ratio of successful executions
        :param bound_inputs: The set of inputs that should be bound to the map task
        :param bound_inputs_values: Inputs that are bound to the array node and will not be mapped over
        :param run_all_sub_nodes: If True, all sub-nodes will run to completion even after the failure threshold is met
        :param kwargs: Additional keyword arguments to pass to the base class
        """
        self._partial = None
        if isinstance(python_function_task, functools.partial):
            self._partial = python_function_task
            actual_task = self._partial.func
        else:
            actual_task = python_function_task

        # TODO: add support for other Flyte entities
        if not (
            (
                isinstance(actual_task, PythonFunctionTask)
                and actual_task.execution_mode == PythonFunctionTask.ExecutionBehavior.DEFAULT
            )
            or isinstance(actual_task, PythonInstanceTask)
        ):
            raise ValueError(
                "Only PythonFunctionTask with default execution mode (not @dynamic or @eager) and PythonInstanceTask are supported in map tasks."
            )

        n_outputs = len(actual_task.python_interface.outputs)
        if n_outputs > 1:
            raise ValueError("Only tasks with a single output are supported in map tasks.")

        # Note, bound_inputs are passed in during run time when executing the task
        # so both values shouldn't be set at the same time
        if bound_inputs and bound_inputs_values:
            if bound_inputs != set(bound_inputs_values):
                raise ValueError("bound_inputs and bound_inputs_values should have the same keys if both set")

        self._bound_inputs: Set[str] = bound_inputs or set(bound_inputs) if bound_inputs else set()
        if self._partial:
            self._bound_inputs.update(self._partial.keywords.keys())

        self._bound_inputs_values: Dict[str, Any] = bound_inputs_values or {}
        if self._bound_inputs_values:
            # bounded input values override any collisions w/ partials
            self._bound_inputs.update(set(self._bound_inputs_values))

        # Transform the interface to List[Optional[T]] in case `min_success_ratio` is set
        output_as_list_of_optionals = min_success_ratio is not None and min_success_ratio != 1 and n_outputs == 1
        collection_interface = transform_interface_to_list_interface(
            actual_task.python_interface, self._bound_inputs, set(), output_as_list_of_optionals
        )
