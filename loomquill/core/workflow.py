from __future__ import annotations

import asyncio
import inspect
import typing
from dataclasses import dataclass
from enum import Enum
from functools import update_wrapper
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple, Type, Union, cast, overload

from typing_extensions import ParamSpec  # type: ignore
from typing_inspect import is_optional_type

from flytekit.core import constants as _common_constants
from flytekit.core import launch_plan as _annotated_launch_plan
from flytekit.core.base_task import PythonTask, Task
from flytekit.core.class_based_resolver import ClassStorageTaskResolver
from flytekit.core.condition import ConditionalSection, conditional
from flytekit.core.context_manager import (
    CompilationState,
    ExecutionState,
    FlyteContext,
    FlyteContextManager,
    FlyteEntities,
)
from flytekit.core.docstring import Docstring
from flytekit.core.interface import (
    Interface,
    transform_function_to_interface,
    transform_interface_to_typed_interface,
)
from flytekit.core.node import Node
from flytekit.core.options import Options
from flytekit.core.promise import (
    NodeOutput,
    Promise,
    VoidPromise,
    binding_from_python_std,
    create_task_output,
    extract_obj_name,
    flyte_entity_call_handler,
    translate_inputs_to_literals,
)
from flytekit.core.python_auto_container import PythonAutoContainerTask
from flytekit.core.reference_entity import ReferenceEntity, WorkflowReference
from flytekit.core.tracker import extract_task_module
from flytekit.core.type_engine import TypeEngine
from flytekit.exceptions.user import (
    FlyteFailureNodeInputMismatchException,
    FlyteValidationException,
    FlyteValueException,
)
from flytekit.loggers import logger
from flytekit.models import interface as _interface_models
from flytekit.models import literals as _literal_models
from flytekit.models.core import workflow as _workflow_model
from flytekit.models.documentation import Description, Documentation
from flytekit.types.error import FlyteError

GLOBAL_START_NODE = Node(
    id=_common_constants.GLOBAL_INPUT_NODE_ID,
    metadata=None,
    bindings=[],
    upstream_nodes=[],
    flyte_entity=None,
)

P = ParamSpec("P")
T = typing.TypeVar("T")
FuncOut = typing.TypeVar("FuncOut")


class WorkflowFailurePolicy(Enum):
    """
    Defines the behavior for a workflow execution in the case of an observed node execution failure. By default, a
    workflow execution will immediately enter a failed state if a component node fails.
    """

    #: Causes the entire workflow execution to fail once a component node fails.
    FAIL_IMMEDIATELY = _workflow_model.WorkflowMetadata.OnFailurePolicy.FAIL_IMMEDIATELY

    #: Will proceed to run any remaining runnable nodes once a component node fails.
    FAIL_AFTER_EXECUTABLE_NODES_COMPLETE = (
        _workflow_model.WorkflowMetadata.OnFailurePolicy.FAIL_AFTER_EXECUTABLE_NODES_COMPLETE
    )


@dataclass
class WorkflowMetadata(object):
    on_failure: WorkflowFailurePolicy

    def __post_init__(self):
        if (
            self.on_failure != WorkflowFailurePolicy.FAIL_IMMEDIATELY
            and self.on_failure != WorkflowFailurePolicy.FAIL_AFTER_EXECUTABLE_NODES_COMPLETE
        ):
            raise FlyteValidationException(f"Failure policy {self.on_failure} not acceptable")

    def to_flyte_model(self):
        if self.on_failure == WorkflowFailurePolicy.FAIL_IMMEDIATELY:
            on_failure = 0
        else:
            on_failure = 1
        return _workflow_model.WorkflowMetadata(on_failure=on_failure)


@dataclass
class WorkflowMetadataDefaults(object):
    """
    This class is similarly named to the one above. Please see the IDL for more information but essentially, this
    WorkflowMetadataDefaults class represents the defaults that are handed down to a workflow's tasks, whereas
    WorkflowMetadata represents metadata about the workflow itself.
    """

    interruptible: bool

    def __post_init__(self):
        # TODO: Get mypy working so we don't have to worry about these checks
        if self.interruptible is not True and self.interruptible is not False:
            raise FlyteValidationException(f"Interruptible must be boolean, {self.interruptible} invalid")

    def to_flyte_model(self):
        return _workflow_model.WorkflowMetadataDefaults(interruptible=self.interruptible)


def construct_input_promises(inputs: List[str]) -> Dict[str, Promise]:
    return {
        input_name: Promise(var=input_name, val=NodeOutput(node=GLOBAL_START_NODE, var=input_name))
        for input_name in inputs
    }


def get_promise(binding_data: _literal_models.BindingData, outputs_cache: Dict[Node, Dict[str, Promise]]) -> Promise:
    """
    This is a helper function that will turn a binding into a Promise object, using a lookup map. Please see
    get_promise_map for the rest of the details.
    """
    if binding_data.promise is not None:
        if not isinstance(binding_data.promise, NodeOutput):
            raise FlyteValidationException(
                f"Binding data Promises have to be of the NodeOutput type {type(binding_data.promise)} found"
            )
        # b.var is the name of the input to the task
        # binding_data.promise.var is the name of the upstream node's output we want
        return outputs_cache[binding_data.promise.node][binding_data.promise.var]
    elif binding_data.scalar is not None:
        return Promise(var="placeholder", val=_literal_models.Literal(scalar=binding_data.scalar))
    elif binding_data.collection is not None:
        literals = []
        for bd in binding_data.collection.bindings:
            p = get_promise(bd, outputs_cache)
            literals.append(p.val)
        return Promise(
            var="placeholder",
            val=_literal_models.Literal(collection=_literal_models.LiteralCollection(literals=literals)),
        )
    elif binding_data.map is not None:
        literals = {}  # type: ignore
        for k, bd in binding_data.map.bindings.items():
            p = get_promise(bd, outputs_cache)
            literals[k] = p.val
        return Promise(
            var="placeholder", val=_literal_models.Literal(map=_literal_models.LiteralMap(literals=literals))
        )

    raise FlyteValidationException("Binding type unrecognized.")


def get_promise_map(
    bindings: List[_literal_models.Binding], outputs_cache: Dict[Node, Dict[str, Promise]]
) -> Dict[str, Promise]:
    """
    Local execution of imperatively defined workflows is done node by node. This function will fill in the node's
    entity's input arguments, which are specified using the bindings list, and a map of nodes to its outputs.
    Basically this takes the place of propeller in resolving bindings, pulling in outputs from previously completed
    nodes and filling in the necessary inputs.
    """
    entity_kwargs = {}
    for b in bindings:
        entity_kwargs[b.var] = get_promise(b.binding, outputs_cache)

    return entity_kwargs


class WorkflowBase(object):
    def __init__(
        self,
        name: str,
        workflow_metadata: WorkflowMetadata,
        workflow_metadata_defaults: WorkflowMetadataDefaults,
        python_interface: Interface,
        on_failure: Optional[Union[WorkflowBase, Task]] = None,
        docs: Optional[Documentation] = None,
        default_options: Optional[Options] = None,
        **kwargs,
    ):
        self._name = name
        self._workflow_metadata = workflow_metadata
        self._workflow_metadata_defaults = workflow_metadata_defaults
        self._python_interface = python_interface
        self._interface = transform_interface_to_typed_interface(python_interface)
        self._inputs: Dict[str, Promise] = {}
        self._unbound_inputs: typing.Set[Promise] = set()
        self._nodes: List[Node] = []
        self._output_bindings: List[_literal_models.Binding] = []
        self._on_failure = on_failure
        self._failure_node = None
        self._docs = docs
        self._default_options = default_options

        if self._python_interface.docstring:
            if self.docs is None:
                self._docs = Documentation(
                    short_description=self._python_interface.docstring.short_description,
                    long_description=Description(value=self._python_interface.docstring.long_description),
                )
            else:
                if self._python_interface.docstring.short_description:
                    cast(
                        Documentation, self._docs
                    ).short_description = self._python_interface.docstring.short_description
                if self._python_interface.docstring.long_description:
                    self._docs = Description(value=self._python_interface.docstring.long_description)

        FlyteEntities.entities.append(self)
        super().__init__(**kwargs)

    @property
    def name(self) -> str:
        return self._name

    @property
    def docs(self):
        return self._docs

    @property
    def short_name(self) -> str:
        return extract_obj_name(self._name)

    @property
    def workflow_metadata(self) -> WorkflowMetadata:
        return self._workflow_metadata

    @property
    def workflow_metadata_defaults(self) -> WorkflowMetadataDefaults:
        return self._workflow_metadata_defaults

    @property
    def python_interface(self) -> Interface:
        return self._python_interface

    @property
    def interface(self) -> _interface_models.TypedInterface:
        return self._interface

    @property
    def output_bindings(self) -> List[_literal_models.Binding]:
        self.compile()
        return self._output_bindings

