from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple, Union

from flytekit.core.context_manager import BranchEvalMode, ExecutionState, FlyteContext
from flytekit.core.promise import Promise, VoidPromise, create_and_link_node_from_remote, extract_obj_name
from flytekit.exceptions import user as user_exceptions
from flytekit.loggers import logger
from flytekit.models.core.identifier import Identifier
from flytekit.models.core.workflow import NodeMetadata


class RemoteEntity(ABC):
    def __init__(self, *args, **kwargs):
        # In cases where we make a FlyteTask/Workflow/LaunchPlan from a locally created Python object (i.e. an @task
        # or an @workflow decorated function), we actually have the Python interface, so
        self._python_interface: Optional["Interface"] = None

        super().__init__(*args, **kwargs)

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def id(self) -> Identifier: ...

    def construct_node_metadata(self) -> NodeMetadata:
        """
        Used when constructing the node that encapsulates this task as part of a broader workflow definition.
        """
        return NodeMetadata(
            name=extract_obj_name(self.name),
        )

    def compile(self, ctx: FlyteContext, *args, **kwargs):
        return create_and_link_node_from_remote(ctx, entity=self, **kwargs)  # noqa

    def __call__(self, *args, **kwargs):
        # When a Task is () aka __called__, there are three things we may do:
