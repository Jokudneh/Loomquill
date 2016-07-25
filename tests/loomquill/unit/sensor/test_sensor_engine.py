import tempfile
from dataclasses import asdict

import pytest
from flyteidl.core.execution_pb2 import TaskExecution

import flytekit.models.interface as interface_models
from flytekit.extend.backend.base_connector import ConnectorRegistry
from flytekit.models import literals, types
from flytekit.sensor import FileSensor
from flytekit.sensor.base_sensor import SensorMetadata
from tests.flytekit.unit.extend.test_connector import get_task_template


@pytest.mark.asyncio
async def test_sensor_engine():
    file = tempfile.NamedTemporaryFile()
