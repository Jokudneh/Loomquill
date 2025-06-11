from collections import OrderedDict

import pandas
import pytest
from flytekitplugins.hive.task import HiveConfig, HiveSelectTask, HiveTask

from flytekit import kwtypes, workflow
from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.extend import get_serializable
from flytekit.testing import task_mock
from flytekit.types.schema import FlyteSchema


def test_serialization():
    hive_task = HiveTask(
        name="flytekit.demo.hive_task.hivequery1",
        inputs=kwtypes(my_schema=FlyteSchema, ds=str),
        config=HiveConfig(cluster_label="flyte"),
        query_template="""
            set engine=tez;
            insert overwrite directory '{{ .rawOutputDataPrefix }}' stored as parquet  -- will be unique per retry
            select *
            from blah
            where ds = '{{ .Inputs.ds }}' and uri = '{{ .inputs.my_schema }}'
        """,
        # the schema literal's backend uri will be equal to the value of .raw_output_data
        output_schema_type=FlyteSchema,
    )

    @workflow
    def my_wf(in_schema: FlyteSchema, ds: str) -> FlyteSchema:
