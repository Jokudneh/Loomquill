from datetime import timedelta
from unittest import mock

from flyteidl.core.execution_pb2 import TaskExecution
from flytekitplugins.bigquery.connector import BigQueryMetadata

import flytekit.models.interface as interface_models
from flytekit.extend.backend.base_connector import ConnectorRegistry
from flytekit.interfaces.cli_identifiers import Identifier
from flytekit.models import literals, task, types
from flytekit.models.core.identifier import ResourceType
from flytekit.models.task import Sql, TaskTemplate


@mock.patch("google.cloud.bigquery.job.QueryJob")
@mock.patch("google.cloud.bigquery.Client")
def test_bigquery_connector(mock_client, mock_query_job):
    job_id = "dummy_id"
    mock_instance = mock_client.return_value
    mock_query_job_instance = mock_query_job.return_value
    mock_query_job_instance.state.return_value = "SUCCEEDED"
    mock_query_job_instance.job_id.return_value = job_id

    class MockDestination:
        def __init__(self):
            self.project = "dummy_project"
            self.dataset_id = "dummy_dataset"
            self.table_id = "dummy_table"

