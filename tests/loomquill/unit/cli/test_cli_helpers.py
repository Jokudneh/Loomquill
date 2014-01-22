import mock
import flyteidl.admin.launch_plan_pb2 as _launch_plan_pb2
import flyteidl.admin.task_pb2 as _task_pb2
import flyteidl.admin.workflow_pb2 as _workflow_pb2
import flyteidl.core.tasks_pb2 as _core_task_pb2
from flyteidl.core import identifier_pb2 as _identifier_pb2
from flyteidl.core import workflow_pb2 as _core_workflow_pb2
from flyteidl.core.identifier_pb2 import LAUNCH_PLAN

from flytekit.clis import helpers
from flytekit.clis.helpers import _hydrate_identifier, _hydrate_workflow_template_nodes, hydrate_registration_parameters
from flytekit.clis.sdk_in_container.helpers import parse_copy
from flytekit.constants import CopyFileDetection


def test_parse_args_into_dict():
    sample_args1 = ("input_b=mystr", "input_c=18")
    sample_args2 = ("input_a=mystr===d",)
    sample_args3 = ()
    output = helpers.parse_args_into_dict(sample_args1)
    assert output["input_b"] == "mystr"
    assert output["input_c"] == "18"

    output = helpers.parse_args_into_dict(sample_args2)
    assert output["input_a"] == "mystr===d"

    output = helpers.parse_args_into_dict(sample_args3)
    assert output == {}


def test_strtobool():
    assert not helpers.str2bool("False")
    assert not helpers.str2bool("OFF")
    assert not helpers.str2bool("no")
    assert not helpers.str2bool("0")
    assert helpers.str2bool("t")
    assert helpers.str2bool("true")
    assert helpers.str2bool("stuff")


def test_hydrate_identifier():
    identifier = _hydrate_identifier("project", "domain", "12345", _identifier_pb2.Identifier())
    assert identifier.project == "project"
    assert identifier.domain == "domain"
    assert identifier.version == "12345"

    identifier = _hydrate_identifier(
        "project2", "domain2", "abc", _identifier_pb2.Identifier(project="project", domain="domain", version="12345")
    )
    assert identifier.project == "project"
    assert identifier.domain == "domain"
    assert identifier.version == "12345"

    identifier = _hydrate_identifier(
        "project",
        "domain",
        "12345",
        _identifier_pb2.Identifier(
            project="{{ registration.project }}",
            domain="{{ registration.domain }}",
            version="{{ registration.version }}",
        ),
    )
    assert identifier.project == "project"
    assert identifier.domain == "domain"
    assert identifier.version == "12345"


def test_hydrate_workflow_template():
    workflow_template = _core_workflow_pb2.WorkflowTemplate()
    workflow_template.nodes.append(
        _core_workflow_pb2.Node(
            id="task_node",
            task_node=_core_workflow_pb2.TaskNode(
                reference_id=_identifier_pb2.Identifier(resource_type=_identifier_pb2.TASK)
            ),
        )
    )
    workflow_template.nodes.append(
        _core_workflow_pb2.Node(
            id="launchplan_ref",
            workflow_node=_core_workflow_pb2.WorkflowNode(
                launchplan_ref=_identifier_pb2.Identifier(
                    resource_type=_identifier_pb2.LAUNCH_PLAN,
                    project="project2",
                )
            ),
        )
    )
    workflow_template.nodes.append(
        _core_workflow_pb2.Node(
            id="sub_workflow_ref",
            workflow_node=_core_workflow_pb2.WorkflowNode(
                sub_workflow_ref=_identifier_pb2.Identifier(
                    resource_type=_identifier_pb2.WORKFLOW,
                    project="project2",
                    domain="domain2",
                )
            ),
        )
    )
    workflow_template.nodes.append(
        _core_workflow_pb2.Node(
            id="unchanged",
            task_node=_core_workflow_pb2.TaskNode(
                reference_id=_identifier_pb2.Identifier(
                    resource_type=_identifier_pb2.TASK, project="project2", domain="domain2", version="abc"
                )
            ),
        )
    )
    hydrated_workflow_template = _hydrate_workflow_template_nodes("project", "domain", "12345", workflow_template)
    assert len(hydrated_workflow_template.nodes) == 4
    task_node_identifier = hydrated_workflow_template.nodes[0].task_node.reference_id
    assert task_node_identifier.project == "project"
    assert task_node_identifier.domain == "domain"
    assert task_node_identifier.version == "12345"

    launchplan_ref_identifier = hydrated_workflow_template.nodes[1].workflow_node.launchplan_ref
    assert launchplan_ref_identifier.project == "project2"
