"""
Flytekit map tasks specify how to run a single task across a list of inputs. Map tasks themselves are constructed with
a reference task as well as run-time parameters that limit execution concurrency and failure tolerations.
"""

import functools
import hashlib
import logging
import math
import os
import typing
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Set

from flytekit.configuration import SerializationSettings
from flytekit.core import tracker
from flytekit.core.base_task import PythonTask, Task, TaskResolverMixin
from flytekit.core.constants import CONTAINER_ARRAY_TASK
from flytekit.core.context_manager import ExecutionState, FlyteContext, FlyteContextManager
from flytekit.core.interface import transform_interface_to_list_interface
from flytekit.core.python_function_task import PythonFunctionTask, PythonInstanceTask
from flytekit.core.tracker import TrackedInstance
from flytekit.core.utils import timeit
from flytekit.loggers import logger
from flytekit.models.array_job import ArrayJob
from flytekit.models.interface import Variable
from flytekit.models.task import Container, K8sPod, Sql
from flytekit.tools.module_loader import load_object_from_module


class MapPythonTask(PythonTask):
    """
    A MapPythonTask defines a {{< py_class_ref flytekit.PythonTask >}} which specifies how to run
    an inner {{< py_class_ref flytekit.PythonFunctionTask >}} across a range of inputs in parallel.
    """

    def __init__(
        self,
        python_function_task: typing.Union[PythonFunctionTask, PythonInstanceTask, functools.partial],
        concurrency: Optional[int] = None,
        min_success_ratio: Optional[float] = None,
        bound_inputs: Optional[Set[str]] = None,
        **kwargs,
    ):
        """
        Wrapper that creates a MapPythonTask

        :param python_function_task: This argument is implicitly passed and represents the repeatable function
        :param concurrency: If specified, this limits the number of mapped tasks than can run in parallel to the given
           batch size
        :param min_success_ratio: If specified, this determines the minimum fraction of total jobs which can complete
            successfully before terminating this task and marking it successful
        :param bound_inputs: List[str] specifies a list of variable names within the interface of python_function_task,
              that are already bound and should not be considered as list inputs, but scalar values. This is mostly
              useful at runtime and is passed in by MapTaskResolver. This field is not required when a `partial` method
              is specified. The bound_vars will be auto-deduced from the `partial.keywords`.
        """
        self._partial = None
        if isinstance(python_function_task, functools.partial):
            # TODO: We should be able to support partial tasks with lists as inputs
            for arg in python_function_task.keywords.values():
                if isinstance(arg, list):
                    raise ValueError("Map tasks do not support partial tasks with lists as inputs. ")
            self._partial = python_function_task
            actual_task = self._partial.func
        else:
            actual_task = python_function_task

        if not isinstance(actual_task, PythonFunctionTask):
            if isinstance(actual_task, PythonInstanceTask):
                pass
            else:
                raise ValueError("Map tasks can only compose of PythonFuncton and PythonInstanceTasks currently")

        n_outputs = len(actual_task.python_interface.outputs.keys())
        if n_outputs > 1:
            raise ValueError("Map tasks only accept python function tasks with 0 or 1 outputs")

        self._bound_inputs: typing.Set[str] = set(bound_inputs) if bound_inputs else set()
        if self._partial:
            self._bound_inputs = set(self._partial.keywords.keys())

        # Transform the interface to List[Optional[T]] in case `min_success_ratio` is set
        output_as_list_of_optionals = min_success_ratio is not None and min_success_ratio != 1 and n_outputs == 1
        collection_interface = transform_interface_to_list_interface(
            actual_task.python_interface, self._bound_inputs, set(), output_as_list_of_optionals
        )

        self._run_task: typing.Union[PythonFunctionTask, PythonInstanceTask] = actual_task  # type: ignore
        if isinstance(actual_task, PythonInstanceTask):
            mod = actual_task.task_type
            f = actual_task.lhs
        else:
            _, mod, f, _ = tracker.extract_task_module(typing.cast(PythonFunctionTask, actual_task).task_function)
        sorted_bounded_inputs = ",".join(sorted(self._bound_inputs))
        h = hashlib.md5(sorted_bounded_inputs.encode("utf-8")).hexdigest()
        name = f"{mod}.map_{f}_{h}"

        self._cmd_prefix: typing.Optional[typing.List[str]] = None
        self._max_concurrency: typing.Optional[int] = concurrency
        self._min_success_ratio: typing.Optional[float] = min_success_ratio
        self._array_task_interface = actual_task.python_interface
        if "metadata" not in kwargs and actual_task.metadata:
            kwargs["metadata"] = actual_task.metadata
        if "security_ctx" not in kwargs and actual_task.security_context:
            kwargs["security_ctx"] = actual_task.security_context
        super().__init__(
            name=name,
            interface=collection_interface,
            task_type=CONTAINER_ARRAY_TASK,
            task_config=None,
            task_type_version=1,
            **kwargs,
        )

    @property
    def bound_inputs(self) -> Set[str]:
        return self._bound_inputs

    def get_command(self, settings: SerializationSettings) -> List[str]:
        """
        TODO ADD bound variables to the resolver. Maybe we need a different resolver?
        """
        mt = MapTaskResolver()
