from datetime import datetime, timedelta, timezone

import jsonpickle
import pytest
from airflow.operators.python import PythonOperator
from airflow.sensors.bash import BashSensor
from airflow.sensors.time_sensor import TimeSensor
from flyteidl.core.execution_pb2 import TaskExecution
from flytekitplugins.airflow import AirflowObj
from flytekitplugins.airflow.connector import AirflowConnector, AirflowMetadata

from flytekit import workflow
from flytekit.interfaces.cli_identifiers import Identifier
from flytekit.models import interface as interface_models
from flytekit.models import literals, task
from flytekit.models.core.identifier import ResourceType
from flytekit.models.task import TaskTemplate


def py_func():
    print("airflow python sensor")
    return True
