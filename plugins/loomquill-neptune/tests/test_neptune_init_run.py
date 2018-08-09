from unittest.mock import patch, Mock

from flytekit import Secret, task, current_context
from flytekitplugins.neptune import neptune_init_run
from flytekitplugins.neptune.tracking import _neptune_init_run_class

neptune_api_token = Secret(key="neptune_api_token", group="neptune_group")


def test_get_extra_config():

    @neptune_init_run(project="flytekit/project", secret=neptune_api_token, tags=["my-tag"])
    def my_task() -> bool:
        ...

    config = my_task.get_extra_config()
    assert config[my_task.NEPTUNE_HOST_KEY] == "https://app.neptune.ai"
    assert config[my_task.NEPTUNE_PROJECT_KEY] == "flytekit/project"


@task
@neptune_init_run(project="flytekit/project", secret=neptune_api_token, tags=["my-tag"])
def neptune_task() -> bool:
    ctx = current_context()
    return ctx.neptune_run is not None


@patch("flytekitplugins.neptune.tracking.neptune")
def test_local_project_and_init_run_kwargs(neptune_mock):
    neptune_exists = neptune_task()
    assert neptune_exists

    neptune_mock.init_run.assert_called_with(
