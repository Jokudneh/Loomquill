import datetime
import sys
import typing
from base64 import b64decode
from collections import OrderedDict
from dataclasses import dataclass

import pytest
from flyteidl.core import artifact_id_pb2 as art_id
from flyteidl.core.artifact_id_pb2 import Granularity
from google.protobuf.timestamp_pb2 import Timestamp
from typing_extensions import Annotated, get_args

from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.core.array_node_map_task import map_task
from flytekit.core.artifact import Artifact, Inputs, TimePartition
from flytekit.core.context_manager import ExecutionState, FlyteContext, FlyteContextManager, OutputMetadataTracker
from flytekit.core.interface import detect_artifact
from flytekit.core.launch_plan import LaunchPlan
from flytekit.core.task import task
from flytekit.core.type_engine import TypeEngine
from flytekit.core.workflow import workflow
from flytekit.exceptions.user import FlyteValidationException
from flytekit.tools.translator import get_serializable

if "pandas" not in sys.modules:
    pytest.skip(reason="Requires pandas", allow_module_level=True)

default_img = Image(name="default", fqn="test", tag="tag")
serialization_settings = SerializationSettings(
    project="project",
    domain="domain",
    version="version",
    env=None,
    image_config=ImageConfig(default_image=default_img, images=[default_img]),
)


@dataclass
class TestObject(object):
    text: str
    prefix: str

    def serialize_to_string(self, ctx: FlyteContext, variable_name: str) -> typing.Tuple[str, str]:
        return f"{self.prefix}_meta{variable_name}", self.text


class CustomReturn(object):
    def __init__(self, data):
        self.data = data


def test_basic_option_a_rev():
    import pandas as pd

    a1_t_ab = Artifact(name="my_data", partition_keys=["a", "b"], time_partitioned=True)

    @task
    def t1(
        b_value: str, dt: datetime.datetime
    ) -> Annotated[pd.DataFrame, a1_t_ab(time_partition=Inputs.dt, b=Inputs.b_value, a="manual")]:
        df = pd.DataFrame({"a": [1, 2, 3], "b": [b_value, b_value, b_value]})
        return df

    assert a1_t_ab.time_partition.granularity == Granularity.DAY
    entities = OrderedDict()
    t1_s = get_serializable(entities, serialization_settings, t1)
    assert len(t1_s.template.interface.outputs["o0"].artifact_partial_id.partitions.value) == 2
    p = t1_s.template.interface.outputs["o0"].artifact_partial_id.partitions.value
    assert t1_s.template.interface.outputs["o0"].artifact_partial_id.time_partition is not None
    assert (
        t1_s.template.interface.outputs["o0"].artifact_partial_id.time_partition.granularity == art_id.Granularity.DAY
    )
    assert t1_s.template.interface.outputs["o0"].artifact_partial_id.time_partition.value.input_binding.var == "dt"
    assert p["b"].HasField("input_binding")
    assert p["b"].input_binding.var == "b_value"
    assert p["a"].HasField("static_value")
    assert p["a"].static_value == "manual"
    assert t1_s.template.interface.outputs["o0"].artifact_partial_id.version == ""
    assert t1_s.template.interface.outputs["o0"].artifact_partial_id.artifact_key.name == "my_data"
    assert t1_s.template.interface.outputs["o0"].artifact_partial_id.artifact_key.project == ""


def test_basic_multiple_call():
    import pandas as pd

    a1_t_ab = Artifact(name="my_data", partition_keys=["a", "b"], time_partitioned=True)

    @task
    def t1(
        b_value: str, dt: datetime.datetime
    ) -> Annotated[pd.DataFrame, a1_t_ab(b=Inputs.b_value)(time_partition=Inputs.dt)(a="manual")]:
        df = pd.DataFrame({"a": [1, 2, 3], "b": [b_value, b_value, b_value]})
        return df

    assert a1_t_ab.time_partition.granularity == Granularity.DAY
    entities = OrderedDict()
    t1_s = get_serializable(entities, serialization_settings, t1)
    assert len(t1_s.template.interface.outputs["o0"].artifact_partial_id.partitions.value) == 2
    p = t1_s.template.interface.outputs["o0"].artifact_partial_id.partitions.value
    assert t1_s.template.interface.outputs["o0"].artifact_partial_id.time_partition is not None
    assert (
        t1_s.template.interface.outputs["o0"].artifact_partial_id.time_partition.granularity == art_id.Granularity.DAY
    )
    assert t1_s.template.interface.outputs["o0"].artifact_partial_id.time_partition.value.input_binding.var == "dt"
    assert p["b"].HasField("input_binding")
    assert p["b"].input_binding.var == "b_value"
    assert p["a"].HasField("static_value")
    assert p["a"].static_value == "manual"
    assert t1_s.template.interface.outputs["o0"].artifact_partial_id.version == ""
    assert t1_s.template.interface.outputs["o0"].artifact_partial_id.artifact_key.name == "my_data"
    assert t1_s.template.interface.outputs["o0"].artifact_partial_id.artifact_key.project == ""


def test_args_getting():
    a1 = Artifact(name="argstst")
    a1_called = a1()
    x = Annotated[int, a1_called]
    gotten = get_args(x)
    assert len(gotten) == 2
    assert gotten[1] is a1_called
    detected = detect_artifact(get_args(int))
    assert detected is None
    detected = detect_artifact(get_args(x))
    assert detected == a1_called.to_partial_artifact_id()


def test_basic_option_no_tp():
    import pandas as pd

    a1_t_ab = Artifact(name="my_data", partition_keys=["a", "b"])
    assert not a1_t_ab.time_partitioned

    # trying to bind to a time partition when not so raises an error.
    with pytest.raises(ValueError):

        @task
        def t1x(
            b_value: str, dt: datetime.datetime
        ) -> Annotated[pd.DataFrame, a1_t_ab(time_partition=Inputs.dt, b=Inputs.b_value, a="manual")]:
            df = pd.DataFrame({"a": [1, 2, 3], "b": [b_value, b_value, b_value]})
            return df

    @task
    def t1(b_value: str, dt: datetime.datetime) -> Annotated[pd.DataFrame, a1_t_ab(b=Inputs.b_value, a="manual")]:
        df = pd.DataFrame({"a": [1, 2, 3], "b": [b_value, b_value, b_value]})
        return df

    entities = OrderedDict()
    t1_s = get_serializable(entities, serialization_settings, t1)
    assert len(t1_s.template.interface.outputs["o0"].artifact_partial_id.partitions.value) == 2
    p = t1_s.template.interface.outputs["o0"].artifact_partial_id.partitions.value
    assert t1_s.template.interface.outputs["o0"].artifact_partial_id.HasField("time_partition") is False
    assert p["b"].HasField("input_binding")


def test_basic_option_hardcoded_tp():
    a1_t_ab = Artifact(name="my_data", time_partitioned=True)

    dt = datetime.datetime.strptime("04/05/2063", "%m/%d/%Y")

    id_spec = a1_t_ab(time_partition=dt)
    assert id_spec.partitions is None
    assert id_spec.time_partition.value.HasField("time_value")


def test_bound_ness():
    a1_a = Artifact(name="my_data", partition_keys=["a"])
    q = a1_a.query()
    assert not q.bound

    q = a1_a.query(a="hi")
    assert q.bound


def test_bound_ness_time():
    a1_t = Artifact(name="my_data", time_partitioned=True)
    q = a1_t.query()
    assert not q.bound

    q = a1_t.query(time_partition=Inputs.dt)
    assert q.bound


def test_basic_option_a():
    import pandas as pd

    a1_t_ab = Artifact(name="my_data", partition_keys=["a", "b"], time_partitioned=True)

    @task
    def t1(
        b_value: str, dt: datetime.datetime
    ) -> Annotated[pd.DataFrame, a1_t_ab(b=Inputs.b_value, a="const", time_partition=Inputs.dt)]:
        df = pd.DataFrame({"a": [1, 2, 3], "b": [b_value, b_value, b_value]})
        return df

    entities = OrderedDict()
    t1_s = get_serializable(entities, serialization_settings, t1)
    assert len(t1_s.template.interface.outputs["o0"].artifact_partial_id.partitions.value) == 2
