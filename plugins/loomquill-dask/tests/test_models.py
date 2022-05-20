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


@pytest.fixture
def workers(image: str, resources: _task.Resources) -> models.WorkerGroup:
    return models.WorkerGroup(number_of_workers=123, image=image, resources=resources)


def test_create_scheduler_to_flyte_idl_no_optional(image: str, resources: _task.Resources):
