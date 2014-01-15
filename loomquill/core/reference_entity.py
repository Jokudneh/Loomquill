from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, Type, Union

from flytekit.core.context_manager import BranchEvalMode, ExecutionState, FlyteContext
from flytekit.core.interface import Interface, transform_interface_to_typed_interface
from flytekit.core.promise import (
    Promise,
    VoidPromise,
    create_and_link_node,
    create_task_output,
    extract_obj_name,
    translate_inputs_to_literals,
)
from flytekit.core.type_engine import TypeEngine
from flytekit.loggers import logger
from flytekit.models import interface as _interface_models
from flytekit.models import literals as _literal_models
from flytekit.models.core import identifier as _identifier_model
from flytekit.models.core import workflow as _workflow_model


@dataclass  # type: ignore
class Reference(ABC):
    project: str
    domain: str
    name: str
    version: str

    def __post_init__(self):
        self._id = _identifier_model.Identifier(self.resource_type, self.project, self.domain, self.name, self.version)

    @property
    def id(self) -> _identifier_model.Identifier:
        return self._id

    @property
    @abstractmethod
    def resource_type(self) -> int: ...


@dataclass
class TaskReference(Reference):
    """A reference object containing metadata that points to a remote task."""

    @property
    def resource_type(self) -> int:
        return _identifier_model.ResourceType.TASK


@dataclass
class LaunchPlanReference(Reference):
    """A reference object containing metadata that points to a remote launch plan."""

    @property
    def resource_type(self) -> int:
        return _identifier_model.ResourceType.LAUNCH_PLAN


@dataclass
