import typing
from collections import OrderedDict
from datetime import timedelta
from io import StringIO

from mock import patch

from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.core.condition import conditional
from flytekit.core.context_manager import ExecutionState, FlyteContextManager
from flytekit.core.dynamic_workflow_task import dynamic
from flytekit.core.gate import approve, sleep, wait_for_input
from flytekit.core.task import task
from flytekit.core.type_engine import TypeEngine
from flytekit.core.workflow import workflow
from flytekit.remote.entities import FlyteWorkflow
from flytekit.tools.translator import gather_dependent_entities, get_serializable

default_img = Image(name="default", fqn="test", tag="tag")
serialization_settings = SerializationSettings(
    project="project",
    domain="domain",
    version="version",
    env=None,
    image_config=ImageConfig(default_image=default_img, images=[default_img]),
)


def test_basic_sleep():
    @task
    def t1(a: int) -> int:
        return a + 5

    @workflow
    def wf_sleep() -> int:
        x = sleep(timedelta(seconds=10))
        b = t1(a=5)
        x >> b
        return b

    wf_spec = get_serializable(OrderedDict(), serialization_settings, wf_sleep)
    assert len(wf_spec.template.nodes) == 2
    wf_spec.template.nodes[0].gate_node is not None
    wf_spec.template.nodes[0].gate_node.sleep.duration == timedelta(seconds=10)
    wf_spec.template.nodes[1].upstream_node_ids == ["n0"]


def test_basic_signal():
    @task
    def t1(a: int) -> int:
        return a + 5

    @task
    def t2(a: int) -> int:
        return a + 6

    @workflow
    def wf(a: int) -> typing.Tuple[int, int, int]:
        x = t1(a=a)
        s1 = wait_for_input("my-signal-name", timeout=timedelta(hours=1), expected_type=bool)
        s2 = wait_for_input("my-signal-name-2", timeout=timedelta(hours=2), expected_type=int)
        z = t1(a=5)
        y = t2(a=s2)
        q = t2(a=approve(y, "approvalfory", timeout=timedelta(hours=2)))
        x >> s1
        s1 >> z

