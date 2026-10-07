import typing

from flyteidl.admin import workflow_pb2 as _admin_workflow

from flytekit.models import common as _common
from flytekit.models.core import compiler as _compiler_models
from flytekit.models.core import identifier as _identifier
from flytekit.models.core import workflow as _core_workflow
from flytekit.models.documentation import Documentation


class WorkflowSpec(_common.FlyteIdlEntity):
    def __init__(
        self,
        template: _core_workflow.WorkflowTemplate,
        sub_workflows: typing.List[_core_workflow.WorkflowTemplate],
        docs: typing.Optional[Documentation] = None,
    ):
        """
        This object fully encapsulates the specification of a workflow
        :param flytekit.models.core.workflow.WorkflowTemplate template:
        :param list[flytekit.models.core.workflow.WorkflowTemplate] sub_workflows:
        """
        self._template = template
        self._sub_workflows = sub_workflows
        self._docs = docs

    @property
    def template(self):
        """
        :rtype: flytekit.models.core.workflow.WorkflowTemplate
        """
        return self._template

    @property
    def sub_workflows(self):
        """
        :rtype: list[flytekit.models.core.workflow.WorkflowTemplate]
        """
        return self._sub_workflows

    @property
    def docs(self):
        """
        :rtype: Description entity for the workflow
        """
        return self._docs
