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
