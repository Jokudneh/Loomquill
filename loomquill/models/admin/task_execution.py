from flyteidl.admin import task_execution_pb2 as _task_execution_pb2

from flytekit.models import common as _common
from flytekit.models import event as _event
from flytekit.models.core import execution as _execution
from flytekit.models.core import identifier as _identifier


class TaskExecutionClosure(_common.FlyteIdlEntity):
    def __init__(
        self,
        phase,
        logs,
        started_at,
        duration,
        created_at,
        updated_at,
        output_uri=None,
        error=None,
        metadata=None,
    ):
        """
        :param int phase: Enum value from flytekit.models.core.execution.TaskExecutionPhase
        :param list[flytekit.models.core.execution.TaskLog] logs: List of all logs associated with the execution.
        :param datetime.datetime started_at:
        :param datetime.timedelta duration:
        :param datetime.datetime created_at:
        :param datetime.datetime updated_at:
        :param Text output_uri: If task is successful and in terminal state, this will be the path to the output
            literals.
        :param flytekit.models.core.execution.ExecutionError error: If task has failed and in terminal state, this will
            be set to the error encountered.
        :param flytekit.models.event.TaskExecutionMetadata metadata: Metadata associated with the task execution.
        """
        self._phase = phase
        self._logs = logs
        self._started_at = started_at
        self._duration = duration
        self._created_at = created_at
        self._updated_at = updated_at
        self._output_uri = output_uri
        self._error = error
        self._metadata = metadata

    @property
    def phase(self):
        """
        Enum value from flytekit.models.core.execution.TaskExecutionPhase
        :rtype: flytekit.models.core.execution.TaskExecutionPhase
        """
        return self._phase

    @property
    def logs(self):
        """
        :rtype: list[flytekit.models.core.execution.TaskLog]
        """
        return self._logs

    @property
