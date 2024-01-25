from flyteidl.admin import common_pb2 as _common_pb2

from flytekit.core import notification
from flytekit.core.launch_plan import LaunchPlan
from flytekit.core.task import task
from flytekit.core.workflow import workflow
from flytekit.models import common as _common_model
from flytekit.models.core import execution as _execution_model

_workflow_execution_succeeded = _execution_model.WorkflowExecutionPhase.SUCCEEDED


def test_pager_duty_notification():
    pager_duty_notif = notification.PagerDuty(
        phases=[_workflow_execution_succeeded], recipients_email=["my-team@pagerduty.com"]
    )
    assert pager_duty_notif.to_flyte_idl() == _common_pb2.Notification(
        phases=[_workflow_execution_succeeded],
        email=None,
