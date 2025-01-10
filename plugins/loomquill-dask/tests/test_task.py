import pytest
from flytekitplugins.dask import Dask, Scheduler, WorkerGroup

from flytekit import PythonFunctionTask, Resources, task
from flytekit.configuration import Image, ImageConfig, SerializationSettings


@pytest.fixture
def serialization_settings() -> SerializationSettings:
    default_img = Image(name="default", fqn="test", tag="tag")
    settings = SerializationSettings(
        project="project",
        domain="domain",
        version="version",
        env={"FOO": "baz"},
        image_config=ImageConfig(default_image=default_img, images=[default_img]),
    )
    return settings


def test_dask_task_with_default_config(serialization_settings: SerializationSettings):
    task_config = Dask()

    @task(task_config=task_config)
    def dask_task():
        pass

    # Helping type completion in PyCharm
    dask_task: PythonFunctionTask[Dask]

    assert dask_task.task_config == task_config
