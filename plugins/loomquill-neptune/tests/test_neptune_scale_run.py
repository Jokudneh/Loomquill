from unittest.mock import patch, Mock

from flytekit import Secret, task, current_context
from flytekitplugins.neptune import neptune_scale_run
from flytekitplugins.neptune.scale_tracking import _neptune_scale_run_class

neptune_api_token = Secret(key="neptune_api_token", group="neptune_group")


def test_get_extra_config():

    @neptune_scale_run(project="flytekit/project", secret=neptune_api_token, run_id="my-task")
    def my_task() -> bool: ...

    config = my_task.get_extra_config()
    assert config[my_task.NEPTUNE_PROJECT] == "flytekit/project"
    assert config[my_task.NEPTUNE_RUN_ID] == "my-task"

    @neptune_scale_run(
        project="flytekit/project",
        secret=neptune_api_token,
        experiment_name="my-experiment",
    )
    def my_task() -> bool: ...

    config = my_task.get_extra_config()
    assert config[my_task.NEPTUNE_PROJECT] == "flytekit/project"


@task
@neptune_scale_run(project="flytekit/project", secret=neptune_api_token)
def neptune_task() -> bool:
    ctx = current_context()
    return ctx.neptune_run is not None


@patch("flytekitplugins.neptune.scale_tracking.neptune_scale")
def test_local_project_and_init_run_kwargs(neptune_scale_mock):
    neptune_exists = neptune_task()
    assert neptune_exists

    neptune_scale_mock.Run.assert_called_with(
        run_id=None, experiment_name=None, project="flytekit/project"
    )
