import jsonpickle
from airflow.operators.bash import BashOperator
from airflow.providers.apache.beam.operators.beam import BeamRunJavaPipelineOperator, BeamRunPythonPipelineOperator
from airflow.providers.google.cloud.operators.dataproc import DataprocCreateClusterOperator
from airflow.sensors.bash import BashSensor
from airflow.sensors.time_sensor import TimeSensor
from airflow.utils.context import Context
from flytekitplugins.airflow.task import (
    AirflowContainerTask,
    AirflowObj,
    AirflowTask,
    _flyte_operator,
    _is_deferrable,
    airflow_task_resolver,
)
from mock import mock

from flytekit import FlyteContextManager
from flytekit.configuration import ImageConfig, SerializationSettings
from flytekit.core import context_manager


def test_xcom_push():
    ctx = FlyteContextManager.current_context()
    ctx.user_space_params._attrs = {}

    execution_state = ctx.execution_state.with_params(
        user_space_params=ctx.user_space_params.new_builder()
        .add_attr("GET_ORIGINAL_TASK", True)
