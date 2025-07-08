from flytekit.models.core import identifier


def test_identifier():
    obj = identifier.Identifier(identifier.ResourceType.TASK, "project", "domain", "name", "version")
    assert obj.project == "project"
    assert obj.domain == "domain"
    assert obj.name == "name"
    assert obj.version == "version"
    assert obj.resource_type == identifier.ResourceType.TASK
    assert obj.resource_type_name() == "TASK"

    obj2 = identifier.Identifier.from_flyte_idl(obj.to_flyte_idl())
    assert obj2 == obj
    assert obj2.project == "project"
    assert obj2.domain == "domain"
    assert obj2.name == "name"
    assert obj2.version == "version"
    assert obj2.resource_type == identifier.ResourceType.TASK
    assert obj2.resource_type_name() == "TASK"


def test_node_execution_identifier():
    wf_exec_id = identifier.WorkflowExecutionIdentifier("project", "domain", "name")
    obj = identifier.NodeExecutionIdentifier("node_id", wf_exec_id)
    assert obj.node_id == "node_id"
    assert obj.execution_id == wf_exec_id

    obj2 = identifier.NodeExecutionIdentifier.from_flyte_idl(obj.to_flyte_idl())
    assert obj2 == obj
    assert obj2.node_id == "node_id"
