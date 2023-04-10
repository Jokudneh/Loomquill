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


class BigQueryTask(AsyncConnectorExecutorMixin, SQLTask[BigQueryConfig]):
    """
    This is the simplest form of a BigQuery Task, that can be used even for tasks that do not produce any output.
    """

    # This task is executed using the BigQuery handler in the backend.
    # https://github.com/flyteorg/flyteplugins/blob/43623826fb189fa64dc4cb53e7025b517d911f22/go/tasks/plugins/webapi/bigquery/plugin.go#L34
    _TASK_TYPE = "bigquery_query_job_task"

