from flytekit.models import node_execution as node_execution_models
from flytekit.models.core import catalog, identifier
from tests.flytekit.unit.common_tests.test_workflow_promote import get_compiled_workflow_closure


def test_workflow_node_metadata():
    wf_exec_id = identifier.WorkflowExecutionIdentifier("project", "domain", "name")

    obj = node_execution_models.WorkflowNodeMetadata(execution_id=wf_exec_id)
    assert obj.execution_id is wf_exec_id

    obj2 = node_execution_models.WorkflowNodeMetadata.from_flyte_idl(obj.to_flyte_idl())
    assert obj == obj2


