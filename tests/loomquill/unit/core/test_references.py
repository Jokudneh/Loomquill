import typing
from collections import OrderedDict

import pytest

import flytekit.configuration
from flytekit.configuration import Image, ImageConfig
from flytekit.core import context_manager
from flytekit.core.base_task import kwtypes
from flytekit.core.dynamic_workflow_task import dynamic
from flytekit.core.launch_plan import LaunchPlan, reference_launch_plan
from flytekit.core.promise import VoidPromise
from flytekit.core.reference import get_reference_entity
from flytekit.core.reference_entity import ReferenceEntity, ReferenceSpec, ReferenceTemplate, TaskReference
from flytekit.core.task import reference_task, task
from flytekit.core.testing import patch, task_mock
from flytekit.core.workflow import reference_workflow, workflow
from flytekit.models.core import identifier as _identifier_model
from flytekit.tools.translator import get_serializable


# This is used for docs
def test_ref_docs():
    # docs_ref_start
    ref_entity = get_reference_entity(
        _identifier_model.ResourceType.WORKFLOW,
        "project",
        "dev",
        "my.other.workflow",
        "abc123",
        inputs=kwtypes(a=str, b=int),
        outputs={},
    )
    # docs_ref_end

    with pytest.raises(Exception) as e:
        ref_entity()
    assert "You must mock this out" in f"{e}"


@reference_task(
    project="flytesnacks",
    domain="development",
    name="recipes.aaa.simple.join_strings",
    version="553018f39e519bdb2597b652639c30ce16b99c79",
)
def ref_t1(a: typing.List[str]) -> str:
    """
    The empty function acts as a convenient skeleton to make it intuitive to call/reference this task from workflows.
    The interface of the task must match that of the remote task. Otherwise, remote compilation of the workflow will
    fail.
    """
    return "hello"


def test_ref():
    assert ref_t1.id.project == "flytesnacks"
    assert ref_t1.id.domain == "development"
    assert ref_t1.id.name == "recipes.aaa.simple.join_strings"
    assert ref_t1.id.version == "553018f39e519bdb2597b652639c30ce16b99c79"

    serialization_settings = flytekit.configuration.SerializationSettings(
        project="test_proj",
        domain="test_domain",
        version="abc",
        image_config=ImageConfig(Image(name="name", fqn="image", tag="name")),
        env={},
    )
    spec = get_serializable(OrderedDict(), serialization_settings, ref_t1)
    assert isinstance(spec, ReferenceSpec)
    assert isinstance(spec.template, ReferenceTemplate)
    assert spec.template.id == ref_t1.id
    assert spec.template.resource_type == _identifier_model.ResourceType.TASK


def test_ref_task_more():
    @reference_task(
        project="flytesnacks",
        domain="development",
        name="recipes.aaa.simple.join_strings",
        version="553018f39e519bdb2597b652639c30ce16b99c79",
    )
    def ref_t1(a: typing.List[str]) -> str:
        ...

    @workflow
    def wf1(in1: typing.List[str]) -> str:
        return ref_t1(a=in1)

    with pytest.raises(Exception) as e:
        wf1(in1=["hello", "world"])
    assert "You must mock this out" in f"{e}"

    with task_mock(ref_t1) as mock:
        mock.return_value = "hello"
        assert wf1(in1=["hello", "world"]) == "hello"


def test_ref_task_more_2():
    # Test that >> will not break the mock.

    @reference_task(
        project="flytesnacks",
        domain="development",
        name="recipes.aaa.simple.join_strings",
        version="553018f39e519bdb2597b652639c30ce16b99c79",
    )
    def ref_t1(a: typing.List[str]) -> str:
        ...

    @reference_task(
        project="flytesnacks",
        domain="development",
        name="recipes.aaa.simple.join_string_second",
        version="553018f39e519bdb2597b652639c30ce16b99c79",
    )
    def ref_t2(a: typing.List[str]) -> str:
        ...

    @workflow
    def wf1(in1: typing.List[str]) -> str:
        x = ref_t1(a=in1)
        y = ref_t2(a=in1)
        y >> x
        return x

    with task_mock(ref_t1) as mock_x:
        with task_mock(ref_t2) as mock_y:
            mock_y.return_value = "ignored"
            mock_x.return_value = "hello"
            assert wf1(in1=["hello", "world"]) == "hello"

def test_ref_task_positional_args():
    @reference_task(
        project="flytesnacks",
        domain="development",
        name="recipes.aaa.simple.join_strings",
        version="553018f39e519bdb2597b652639c30ce16b99c79",
    )
    def ref_t1(a: typing.List[str]) -> str:
        ...

    @workflow
    def wf1(in1: typing.List[str]) -> str:
        return ref_t1(in1)

    with pytest.raises(Exception) as e:
        wf1(in1=["hello", "world"])
    assert "You must mock this out" in f"{e}"

    with task_mock(ref_t1) as mock:
        mock.return_value = "hello"
        assert wf1(in1=["hello", "world"]) == "hello"
