from collections import OrderedDict

import pytest
from flytekitplugins.snowflake import SnowflakeConfig, SnowflakeTask

from flytekit import kwtypes, workflow
from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.extend import get_serializable
from flytekit.types.schema import FlyteSchema

query_template = """
            insert overwrite directory '{{ .rawOutputDataPrefix }}' stored as parquet
            select *
            from my_table
            where ds = '{{ .Inputs.ds }}'
        """


def test_serialization():
    snowflake_task = SnowflakeTask(
        name="flytekit.demo.snowflake_task.query",
        inputs=kwtypes(ds=str),
        task_config=SnowflakeConfig(
            account="snowflake",
            user="my_user",
            warehouse="my_warehouse",
            schema="my_schema",
            database="my_database",
        ),
        query_template=query_template,
