import math
from typing import TYPE_CHECKING, Any, List, Optional, Set, Tuple, Union

from flyteidl.core import workflow_pb2 as _core_workflow

from flytekit.core import interface as flyte_interface
from flytekit.core.context_manager import ExecutionState, FlyteContext
from flytekit.core.interface import (
    transform_interface_to_list_interface,
    transform_interface_to_typed_interface,
)
from flytekit.core.launch_plan import LaunchPlan, ReferenceLaunchPlan
from flytekit.core.node import Node
from flytekit.core.promise import (
    Promise,
    VoidPromise,
    create_and_link_node,
    create_and_link_node_from_remote,
    flyte_entity_call_handler,
    translate_inputs_to_literals,
)
from flytekit.core.task import ReferenceTask
from flytekit.loggers import logger
from flytekit.models import interface as _interface_models
from flytekit.models import literals as _literal_models
from flytekit.models.core import workflow as _workflow_model
from flytekit.models.literals import Literal, LiteralCollection, Scalar

ARRAY_NODE_SUBNODE_NAME = "array_node_subnode"

if TYPE_CHECKING:
    from flytekit.remote import FlyteLaunchPlan


class ArrayNode:
    def __init__(
        self,
        target: Union[LaunchPlan, ReferenceTask, "FlyteLaunchPlan"],
        bindings: Optional[List[_literal_models.Binding]] = None,
        concurrency: Optional[int] = None,
        min_successes: Optional[int] = None,
        min_success_ratio: Optional[float] = None,
        metadata: Optional[_workflow_model.NodeMetadata] = None,
        run_all_sub_nodes: bool = False,
    ):
        """
        :param target: The target Flyte entity to map over
        :param concurrency: If specified, this limits the number of mapped tasks than can run in parallel to the given batch
            size. If the size of the input exceeds the concurrency value, then multiple batches will be run serially until
            all inputs are processed. If set to 0, this means unbounded concurrency. If left unspecified, this means the
            array node will inherit parallelism from the workflow
        :param min_successes: The minimum number of successful executions. If set, this takes precedence over
            min_success_ratio
        :param min_success_ratio: The minimum ratio of successful executions.
        :param metadata: The metadata for the underlying node
        :param run_all_sub_nodes: If True, all sub-nodes will run to completion even after the failure threshold is met
        """
        from flytekit.remote import FlyteLaunchPlan

        self.target = target
        self._concurrency = concurrency
        self._run_all_sub_nodes = run_all_sub_nodes
        self.id = target.name
        self._bindings = bindings or []
        self.metadata = metadata
        self._data_mode = None
        self._execution_mode = None

        if min_successes is not None:
            self._min_successes = min_successes
            self._min_success_ratio = None
