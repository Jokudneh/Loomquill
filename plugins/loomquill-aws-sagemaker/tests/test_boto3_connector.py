from datetime import datetime, timedelta
from unittest import mock
import json

import pytest
from flyteidl.core.execution_pb2 import TaskExecution

from flytekit import FlyteContext
from flytekit.extend.backend.base_connector import ConnectorRegistry
from flytekit.interaction.string_literals import literal_map_string_repr
from flytekit.interfaces.cli_identifiers import Identifier
from flytekit.models import literals
from flytekit.models.core.identifier import ResourceType
from flytekit.models.task import RuntimeMetadata, TaskMetadata, TaskTemplate

from flytekitplugins.awssagemaker_inference.boto3_mixin import CustomException
from botocore.exceptions import ClientError

idempotence_token = "74443947857331f7"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mock_return_value",
    [
        (
            (
                {
