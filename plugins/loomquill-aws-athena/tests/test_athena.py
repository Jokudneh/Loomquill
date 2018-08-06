from collections import OrderedDict

import pytest
from flytekitplugins.athena import AthenaConfig, AthenaTask

from flytekit import kwtypes, workflow
from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.extend import get_serializable
from flytekit.types.schema import FlyteSchema


def test_serialization():
    athena_task = AthenaTask(
        name="flytekit.demo.athena_task.query",
        inputs=kwtypes(ds=str),
        task_config=AthenaConfig(database="mnist", catalog="my_catalog", workgroup="my_wg"),
        query_template="""
            insert overwrite directory '{{ .rawOutputDataPrefix }}' stored as parquet
            select *
            from blah
            where ds = '{{ .Inputs.ds }}'
        """,
        # the schema literal's backend uri will be equal to the value of .raw_output_data
        output_schema_type=FlyteSchema,
    )
