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
