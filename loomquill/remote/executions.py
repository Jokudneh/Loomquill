from __future__ import annotations

import typing
from abc import abstractmethod
from datetime import timedelta
from typing import Dict, List, Optional, Union

from flytekit.core.type_engine import LiteralsResolver
from flytekit.exceptions import user as user_exceptions
from flytekit.models import execution as execution_models
from flytekit.models import node_execution as node_execution_models
from flytekit.models.admin import task_execution as admin_task_execution_models
from flytekit.models.core import execution as core_execution_models
from flytekit.models.interface import TypedInterface
from flytekit.remote.entities import FlyteTask, FlyteWorkflow


class RemoteExecutionBase(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._inputs: Optional[LiteralsResolver] = None
        self._outputs: Optional[LiteralsResolver] = None

    @property
    def inputs(self) -> Optional[LiteralsResolver]:
        return self._inputs

    @property
    @abstractmethod
    def error(self) -> core_execution_models.ExecutionError: ...

    @property
    @abstractmethod
    def is_done(self) -> bool: ...

    @property
    def outputs(self) -> Optional[LiteralsResolver]:
        """
        :return: Returns the outputs LiteralsResolver to the execution
        :raises: ``FlyteAssertion`` error if execution is in progress or execution ended in error.
        """
        if not self.is_done:
            raise user_exceptions.FlyteAssertion(
                "Please wait until the execution has completed before requesting the outputs."
            )
        if self.error:
            raise user_exceptions.FlyteAssertion(
                "Outputs could not be found because the execution ended in failure. Error message: "
                f"{self.error.message}"
            )

        return self._outputs


class FlyteTaskExecution(RemoteExecutionBase, admin_task_execution_models.TaskExecution):
    """A class encapsulating a task execution being run on a Flyte remote backend."""

    def __init__(self, *args, **kwargs):
        super(FlyteTaskExecution, self).__init__(*args, **kwargs)
        self._flyte_task = None
