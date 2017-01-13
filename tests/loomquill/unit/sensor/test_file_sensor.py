import datetime
import tempfile

import pytest

from flytekit import task, workflow
from flytekit.configuration import ImageConfig, SerializationSettings
from flytekit.core.task import TaskMetadata
from flytekit.sensor.base_sensor import BaseSensor
from flytekit.sensor.file_sensor import FileSensor
from tests.flytekit.unit.test_translator import default_img


def test_sensor_task():
    sensor = FileSensor(name="test_sensor")
    assert sensor.task_type == "sensor"
    settings = SerializationSettings(
        project="project",
        domain="domain",
        version="version",
