from datetime import timedelta
from unittest import mock
from unittest.mock import MagicMock

import pytest
from flyteidl.core.execution_pb2 import TaskExecution
from flytekitplugins.snowflake.connector import SnowflakeJobMetadata

import flytekit.models.interface as interface_models
from flytekit import lazy_module
from flytekit.extend.backend.base_connector import ConnectorRegistry
from flytekit.interfaces.cli_identifiers import Identifier
from flytekit.models import literals, task, types
from flytekit.models.core.identifier import ResourceType
from flytekit.models.task import Sql, TaskTemplate


@mock.patch("flytekitplugins.snowflake.connector.get_private_key", return_value="pb")
@pytest.mark.asyncio
async def test_snowflake_connector(mock_get_private_key):
    query_status_mock = MagicMock()
    query_status_mock.name = "SUCCEEDED"

    # Configure the mock connection to return the mock status object
