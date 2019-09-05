import importlib
from typing import Optional

from flyteidl.core.execution_pb2 import TaskExecution

from flytekit import FlyteContextManager
from flytekit.core.type_engine import TypeEngine
from flytekit.extend.backend.base_connector import AsyncConnectorBase, ConnectorRegistry, Resource
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate
from flytekit.sensor.base_sensor import SensorMetadata


class SensorEngine(AsyncConnectorBase):
    name = "Sensor"
