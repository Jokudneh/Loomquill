import sys
import typing
from collections import OrderedDict

import pytest
from dataclasses import dataclass, fields, field
import flytekit.configuration
from flytekit.configuration import Image, ImageConfig
from flytekit.core.base_task import kwtypes
from flytekit.core.launch_plan import LaunchPlan
from flytekit.core.task import reference_task, task
from flytekit.core.workflow import ImperativeWorkflow, get_promise, workflow
from flytekit.core.python_function_task import EagerFailureHandlerTask
from flytekit.exceptions.user import FlyteValidationException
from flytekit.extras.sqlite3.task import SQLite3Config, SQLite3Task
from flytekit.models import literals as literal_models
from flytekit.tools.translator import get_serializable
from flytekit.types.file import FlyteFile
from flytekit.types.schema import FlyteSchema
from flytekit.models.admin.workflow import WorkflowSpec

default_img = Image(name="default", fqn="test", tag="tag")
serialization_settings = flytekit.configuration.SerializationSettings(
    project="project",
    domain="domain",
    version="version",
    env=None,
    image_config=ImageConfig(default_image=default_img, images=[default_img]),
)


# This is used for docs
def test_imperative():
    # Re import with alias
    from flytekit.core.workflow import ImperativeWorkflow as Workflow  # noqa

    # docs_tasks_start
    @task
    def t1(a: str) -> str:
        return a + " world"

    @task
    def t2():
        print("side effect")

    # docs_tasks_end

    # docs_start
    # Create the workflow with a name. This needs to be unique within the project and takes the place of the function
    # name that's used for regular decorated function-based workflows.
    wb = Workflow(name="my_workflow")
    # Adds a top level input to the workflow. This is like an input to a workflow function.
    wb.add_workflow_input("in1", str)
    # Call your tasks.
    node = wb.add_entity(t1, a=wb.inputs["in1"])
    wb.add_entity(t2)
    # This is analogous to a return statement
    wb.add_workflow_output("from_n0t1", node.outputs["o0"])
    # docs_end

    assert wb(in1="hello") == "hello world"

    wf_spec = get_serializable(OrderedDict(), serialization_settings, wb)
    assert len(wf_spec.template.nodes) == 2
    assert wf_spec.template.nodes[0].task_node is not None
    assert len(wf_spec.template.outputs) == 1
    assert wf_spec.template.outputs[0].var == "from_n0t1"
    assert len(wf_spec.template.interface.inputs) == 1
    assert len(wf_spec.template.interface.outputs) == 1

    # docs_equivalent_start
    nt = typing.NamedTuple("wf_output", [("from_n0t1", str)])

    @workflow
    def my_workflow(in1: str) -> nt:
        x = t1(a=in1)
        t2()
        return nt(x)

    # docs_equivalent_end

    # Create launch plan from wf, that can also be serialized.
    lp = LaunchPlan.create("test_wb", wb)
    lp_model = get_serializable(OrderedDict(), serialization_settings, lp)
    assert lp_model.spec.workflow_id.name == "my_workflow"

    wb2 = ImperativeWorkflow(name="parent.imperative")
    p_in1 = wb2.add_workflow_input("p_in1", str)
    p_node0 = wb2.add_subwf(wb, in1=p_in1)
    wb2.add_workflow_output("parent_wf_output", p_node0.from_n0t1, str)
    wb2_spec = get_serializable(OrderedDict(), serialization_settings, wb2)
    assert len(wb2_spec.template.nodes) == 1
    assert len(wb2_spec.template.interface.inputs) == 1
    assert wb2_spec.template.interface.inputs["p_in1"].type.simple is not None
    assert len(wb2_spec.template.interface.outputs) == 1
    assert wb2_spec.template.interface.outputs["parent_wf_output"].type.simple is not None
    assert wb2_spec.template.nodes[0].workflow_node.sub_workflow_ref.name == "my_workflow"
    assert len(wb2_spec.sub_workflows) == 1

    wb3 = ImperativeWorkflow(name="parent.imperative")
    p_in1 = wb3.add_workflow_input("p_in1", str)
    p_node0 = wb3.add_launch_plan(lp, in1=p_in1)
    wb3.add_workflow_output("parent_wf_output", p_node0.from_n0t1, str)
    wb3_spec = get_serializable(OrderedDict(), serialization_settings, wb3)
    assert len(wb3_spec.template.nodes) == 1
    assert len(wb3_spec.template.interface.inputs) == 1
    assert wb3_spec.template.interface.inputs["p_in1"].type.simple is not None
    assert len(wb3_spec.template.interface.outputs) == 1
    assert wb3_spec.template.interface.outputs["parent_wf_output"].type.simple is not None
    assert wb3_spec.template.nodes[0].workflow_node.launchplan_ref.name == "test_wb"


def test_imperative_list_bound():
    @task
    def t1(a: typing.List[int]) -> int:
