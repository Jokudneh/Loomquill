from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

from google.protobuf import json_format
from google.protobuf.struct_pb2 import Struct

from flytekit import lazy_module
from flytekit.configuration import SerializationSettings
from flytekit.extend import SQLTask
from flytekit.extend.backend.base_connector import AsyncConnectorExecutorMixin
from flytekit.models import task as _task_model
from flytekit.types.structured import StructuredDataset

bigquery = lazy_module("google.cloud.bigquery")


@dataclass
class BigQueryConfig(object):
    """
    BigQueryConfig should be used to configure a BigQuery Task.
    """

    ProjectID: str
    Location: Optional[str] = None
    QueryJobConfig: Optional[bigquery.QueryJobConfig] = None

