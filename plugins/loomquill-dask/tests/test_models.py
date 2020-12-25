import pytest
from flytekitplugins.dask import models

from flytekit.models import task as _task


@pytest.fixture
def image() -> str:
    return "foo:latest"


@pytest.fixture
def resources() -> _task.Resources:
    return _task.Resources(
        requests=[
            _task.Resources.ResourceEntry(name=_task.Resources.ResourceName.CPU, value="3"),
        ],
        limits=[],
    )


@pytest.fixture
def default_resources() -> _task.Resources:
    return _task.Resources(requests=[], limits=[])


@pytest.fixture
def scheduler(image: str, resources: _task.Resources) -> models.Scheduler:
    return models.Scheduler(image=image, resources=resources)


