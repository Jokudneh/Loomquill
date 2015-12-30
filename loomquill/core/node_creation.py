from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Union

from flytekit.core.base_task import PythonTask
from flytekit.core.context_manager import BranchEvalMode, ExecutionState, FlyteContext
from flytekit.core.launch_plan import LaunchPlan
from flytekit.core.node import Node
from flytekit.core.promise import VoidPromise
from flytekit.core.workflow import WorkflowBase
from flytekit.exceptions import user as _user_exceptions
from flytekit.loggers import logger
from flytekit.utils.asyn import run_sync

if TYPE_CHECKING:
    from flytekit.remote.remote_callable import RemoteEntity


# This file exists instead of moving to node.py because it needs Task/Workflow/LaunchPlan and those depend on Node


def create_node(
    entity: Union[PythonTask, LaunchPlan, WorkflowBase, RemoteEntity], *args, **kwargs
) -> Union[Node, VoidPromise]:
    """
    This is the function you want to call if you need to specify dependencies between tasks that don't consume and/or
    don't produce outputs. For example, if you have t1() and t2(), both of which do not take in nor produce any
    outputs, how do you specify that t2 should run before t1? ::

        t1_node = create_node(t1)
        t2_node = create_node(t2)

        t2_node.runs_before(t1_node)
        # OR
        t2_node >> t1_node

