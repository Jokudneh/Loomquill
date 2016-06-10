from flyteidl.core import workflow_closure_pb2 as _workflow_closure_pb2

from flytekit.models import common as _common
from flytekit.models import task as _task_models
from flytekit.models.core import workflow as _core_workflow_models


class WorkflowClosure(_common.FlyteIdlEntity):
    def __init__(self, workflow, tasks=None):
        """
        :param flytekit.models.core.workflow.WorkflowTemplate workflow: Workflow template
        :param list[flytekit.models.task.TaskTemplate] tasks: [Optional]
