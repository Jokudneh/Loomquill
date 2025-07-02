import typing
from collections import OrderedDict

import pytest

from flytekit import dynamic
from flytekit.configuration import FastSerializationSettings, Image, ImageConfig, SerializationSettings
from flytekit.core import context_manager
from flytekit.core.context_manager import ExecutionState
from flytekit.core.launch_plan import LaunchPlan
from flytekit.core.task import task
from flytekit.core.type_engine import TypeEngine
from flytekit.core.workflow import workflow
from flytekit.exceptions.user import FlyteAssertion
from flytekit.models.admin.workflow import WorkflowSpec
from flytekit.models.task import TaskSpec
from flytekit.remote import FlyteLaunchPlan, FlyteTask, FlyteWorkflow
from flytekit.remote.interface import TypedInterface
from flytekit.tools.translator import gather_dependent_entities, get_serializable

default_img = Image(name="default", fqn="test", tag="tag")
serialization_settings = SerializationSettings(
    project="project",
    domain="domain",
    version="version",
    env=None,
    image_config=ImageConfig(default_image=default_img, images=[default_img]),
)


@task
def t1(a: int) -> int:
    return a + 2


@task
def t2(a: int, b: str) -> str:
    return b + str(a)


@workflow
def sub_wf(a: int, b: str) -> (int, str):
    x = t1(a=a)
    d = t2(a=x, b=b)
    return x, d


t1_spec = get_serializable(OrderedDict(), serialization_settings, t1)
ft = FlyteTask.promote_from_model(t1_spec.template)


def test_fetched_task():
    @workflow
    def wf(a: int) -> int:
        return ft(a=a).with_overrides(node_name="foobar")

    # Should not work unless mocked out.
