import mock
import pytest
import datetime
from flytekit.core.task import task
from flytekit.remote.remote import FlyteRemote
from flytekit.core.worker_queue import Controller, WorkItem, ItemStatus, Update
from flytekit.configuration import ImageConfig, LocalConfig, SerializationSettings, Image
from flytekit.utils.asyn import loop_manager
from flytekit.models.execution import ExecutionSpec, ExecutionClosure, ExecutionMetadata, NotificationList, Execution, AbortMetadata
from flytekit.models.core import identifier
from flytekit.remote.executions import FlyteWorkflowExecution
from flytekit.models import common as common_models
from flytekit.models.core import execution
from flytekit.exceptions.eager import EagerException


def _mock_reconcile(update: Update):
    update.status = ItemStatus.SUCCESS
    update.wf_exec = mock.MagicMock()
    # This is how the controller pulls the result from a successful execution
    update.wf_exec.outputs.as_python_native.return_value = "hello"


@pytest.mark.asyncio
@mock.patch("flytekit.core.worker_queue.Controller.reconcile_one", side_effect=_mock_reconcile)
async def test_controller(mock_reconcile):
    print(f"ID mock_reconcile {id(mock_reconcile)}")
    mock_reconcile.return_value = 123

    @task
    def t1() -> str:
        return "hello"

    remote = FlyteRemote.for_sandbox()
    ss = SerializationSettings(
        image_config=ImageConfig.auto_default_image(),
    )
    c = Controller(remote, ss, tag="exec-id", root_tag="exec-id", exec_prefix="e-unit-test")

    async def fake_eager():
        f = c.add(entity=t1, input_kwargs={})
        res = await f
        assert res == "hello"

    await fake_eager()


@pytest.mark.asyncio
@mock.patch("flytekit.core.worker_queue.Controller._execute")
async def test_controller_launch(mock_thread_target):
    @task
    def t2() -> str:
        return "hello"

    def _mock_thread_target(*args, **kwargs):
        print("in thread")
    mock_thread_target.side_effect = _mock_thread_target

    wf_exec = mock.MagicMock()

    def _mock_execute(
            entity,
            execution_name: str,
            inputs,
            version,
            image_config,
            options,
            envs,
            serialization_settings,
    ):
        assert entity is t2
        assert execution_name.startswith("e-unit-test-t2-")
        assert envs == {'_F_EE_ROOT': 'exec-id'}
        assert serialization_settings == ss
        return wf_exec

    remote = mock.MagicMock()
    remote.execute.side_effect = _mock_execute
