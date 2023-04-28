import json
from datetime import timedelta
from unittest import mock
from unittest.mock import AsyncMock

import pytest
from flyteidl.core.execution_pb2 import TaskExecution
from flytekitplugins.openai.batch.connector import BatchEndpointMetadata
from openai.types import Batch, BatchError, BatchRequestCounts
from openai.types.batch import Errors

from flytekit.extend.backend.base_connector import ConnectorRegistry
from flytekit.interaction.string_literals import literal_map_string_repr
from flytekit.interfaces.cli_identifiers import Identifier
from flytekit.models import literals
from flytekit.models.core.identifier import ResourceType
from flytekit.models.task import RuntimeMetadata, TaskMetadata, TaskTemplate

batch_create_result = Batch(
    id="batch_abc123",
    object="batch",
    endpoint="/v1/completions",
    errors=None,
    input_file_id="file-abc123",
    completion_window="24h",
    status="completed",
    output_file_id="file-cvaTdG",
    error_file_id="file-HOWS94",
    created_at=1711471533,
    in_progress_at=1711471538,
    expires_at=1711557933,
    finalizing_at=1711493133,
    completed_at=1711493163,
    failed_at=None,
    expired_at=None,
    cancelling_at=None,
    cancelled_at=None,
    request_counts=BatchRequestCounts(completed=95, failed=5, total=100),
    metadata={
        "customer_id": "user_123456789",
        "batch_description": "Nightly eval job",
    },
)

batch_retrieve_result = Batch(
    id="batch_abc123",
    object="batch",
    endpoint="/v1/completions",
    errors=None,
    input_file_id="file-abc123",
    completion_window="24h",
    status="completed",
    output_file_id="file-cvaTdG",
    error_file_id="file-HOWS94",
    created_at=1711471533,
    in_progress_at=1711471538,
    expires_at=1711557933,
    finalizing_at=1711493133,
    completed_at=1711493163,
