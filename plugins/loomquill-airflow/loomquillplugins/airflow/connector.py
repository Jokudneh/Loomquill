import asyncio
import typing
from dataclasses import dataclass, field
from typing import List, Optional

import cloudpickle
import jsonpickle
from flyteidl.core.execution_pb2 import TaskExecution, TaskLog
from flytekitplugins.airflow.task import AirflowObj, _get_airflow_instance

from airflow.exceptions import AirflowException, TaskDeferred
from airflow.models import BaseOperator
from airflow.sensors.base import BaseSensorOperator
from airflow.triggers.base import BaseTrigger, TriggerEvent
from airflow.utils.context import Context
from flytekit import logger
from flytekit.exceptions.user import FlyteUserException
from flytekit.extend.backend.base_connector import AsyncConnectorBase, ConnectorRegistry, Resource, ResourceMeta
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate


@dataclass
class AirflowMetadata(ResourceMeta):
    """
    This class is used to store the Airflow task configuration. It is serialized and returned to FlytePropeller.
    """

    airflow_operator: AirflowObj
    airflow_trigger: AirflowObj = field(default=None)
    airflow_trigger_callback: str = field(default=None)
    job_id: typing.Optional[str] = field(default=None)

    def encode(self) -> bytes:
        return cloudpickle.dumps(self)

    @classmethod
    def decode(cls, data: bytes) -> "AirflowMetadata":
        return cloudpickle.loads(data)


class AirflowConnector(AsyncConnectorBase):
    """
    It is used to run Airflow tasks.
    It is registered as an connector in the Connector Registry.
    There are three kinds of Airflow tasks: AirflowOperator, AirflowSensor, and AirflowHook.

    Sensor is always invoked in get method. Calling get method to check if the certain condition is met.
    For example, FileSensor is used to check if the file exists. If file doesn't exist, connector returns
    RUNNING status, otherwise, it returns SUCCEEDED status.
