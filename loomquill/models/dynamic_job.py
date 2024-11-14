from flyteidl.core import dynamic_job_pb2 as _dynamic_job

from flytekit.models import common as _common
from flytekit.models import literals as _literals
from flytekit.models import task as _task
from flytekit.models.core import workflow as _workflow


class DynamicJobSpec(_common.FlyteIdlEntity):
    def __init__(self, tasks, nodes, min_successes, outputs, subworkflows):
        """
        Initializes a new FutureTaskDocument.

        :param list[flytekit.models.task.TaskTemplate] tasks: A collection of unique tasks to execute.
        :param list[flytekit.models.core.workflow.Node] nodes: A collection of task nodes.
        :param int min_successes: An absolute number of the minimum number of successful completions of subtasks. As
            soon as this criteria is met, the future job will be marked as successful and outputs will be computed.
        :param list[flytekit.models.literals.Binding] outputs: Describes how to bind the final output of the future
            task from the
            outputs of executed nodes. The referenced ids in bindings should have the generated id for the subtask.
        :param list[flytekit.models.workflow.WorkflowTemplate] subworkflows: A complete list of task specs referenced
            in nodes.
        """

        self._tasks = tasks
        self._nodes = nodes
        self._min_successes = min_successes
        self._outputs = outputs
        self._subworkflows = subworkflows

    @property
    def tasks(self):
        """
        A collection of tasks to execute.
        :rtype: list[_task.TaskTemplate]
        """
        return self._tasks

    @property
