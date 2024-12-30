import sys
import typing
from collections import OrderedDict
from functools import partial

import pytest

import flytekit.configuration
from flytekit.configuration import Image, ImageConfig
from flytekit.core.array_node_map_task import ArrayNodeMapTaskResolver
from flytekit.core.array_node_map_task import map_task as array_node_map_task
from flytekit.core.dynamic_workflow_task import dynamic
from flytekit.core.legacy_map_task import MapTaskResolver
from flytekit.core.legacy_map_task import map_task as legacy_map_task
from flytekit.core.task import TaskMetadata, task
from flytekit.core.workflow import workflow
from flytekit.tools.translator import gather_dependent_entities, get_serializable

default_img = Image(name="default", fqn="test", tag="tag")
serialization_settings = flytekit.configuration.SerializationSettings(
    project="project",
    domain="domain",
    version="version",
    env=None,
    image_config=ImageConfig(default_image=default_img, images=[default_img]),
)


def test_basics_1():
    @task
    def t1(a: int, b: str, c: float) -> int:
        return a + len(b) + int(c)

    outside_p = partial(t1, b="hello", c=3.14)

    @workflow
    def my_wf_1(a: int) -> typing.Tuple[int, int]:
        inner_partial = partial(t1, b="world", c=2.7)
        out = outside_p(a=a)
        inside = inner_partial(a=a)
        return out, inside

    with pytest.raises(Exception):
        get_serializable(OrderedDict(), serialization_settings, outside_p)

    # check the od todo
    od = OrderedDict()
    wf_1_spec = get_serializable(od, serialization_settings, my_wf_1)
    tts, wspecs, lps = gather_dependent_entities(od)
    tts = [t for t in tts.values()]
    assert len(tts) == 1
    assert len(wf_1_spec.template.nodes) == 2
    assert wf_1_spec.template.nodes[0].task_node.reference_id.name == tts[0].id.name
    assert wf_1_spec.template.nodes[1].task_node.reference_id.name == tts[0].id.name
    assert wf_1_spec.template.nodes[0].inputs[0].binding.promise.var == "a"
    assert wf_1_spec.template.nodes[0].inputs[1].binding.scalar is not None
    assert wf_1_spec.template.nodes[0].inputs[2].binding.scalar is not None

    @task
    def get_str() -> str:
        return "got str"

    bind_c = partial(t1, c=2.7)

    @workflow
    def my_wf_2(a: int) -> int:
        s = get_str()
        inner_partial = partial(bind_c, b=s)
        inside = inner_partial(a=a)
        return inside

    wf_2_spec = get_serializable(OrderedDict(), serialization_settings, my_wf_2)
    assert len(wf_2_spec.template.nodes) == 2


@pytest.mark.parametrize(
    "map_task_fn",
