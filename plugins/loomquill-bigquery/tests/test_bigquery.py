from collections import OrderedDict

import pytest
from flytekitplugins.bigquery import BigQueryConfig, BigQueryTask
from google.cloud.bigquery import QueryJobConfig
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Struct

from flytekit import StructuredDataset, kwtypes, workflow
from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.extend import get_serializable

query_template = "SELECT * FROM `bigquery-public-data.crypto_dogecoin.transactions` WHERE @version = 1 LIMIT 10"


def test_serialization():
    bigquery_task = BigQueryTask(
        name="flytekit.demo.bigquery_task.query",
        inputs=kwtypes(ds=str),
        task_config=BigQueryConfig(
            ProjectID="Flyte", Location="Asia", QueryJobConfig=QueryJobConfig(allow_large_results=True)
        ),
