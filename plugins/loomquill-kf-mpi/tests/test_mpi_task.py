import pytest
from flytekitplugins.kfmpi import CleanPodPolicy, HorovodJob, Launcher, MPIJob, RestartPolicy, RunPolicy, Worker
from flytekitplugins.kfmpi.task import MPIFunctionTask

from flytekit import Resources, task
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


def test_mpi_task(serialization_settings: SerializationSettings):
    @task(
        task_config=MPIJob(num_workers=10, num_launcher_replicas=10, slots=1),
        requests=Resources(cpu="1"),
        cache=True,
        cache_version="1",
    )
    def my_mpi_task(x: int, y: str) -> int:
        return x

    assert my_mpi_task(x=10, y="hello") == 10

    assert my_mpi_task.task_config is not None

    assert my_mpi_task.get_custom(serialization_settings) == {
        "launcherReplicas": {"replicas": 10, "resources": {}},
        "workerReplicas": {"replicas": 10, "resources": {}},
        "slots": 1,
    }
    assert my_mpi_task.task_type == "mpi"
    assert my_mpi_task.task_type_version == 1


def test_mpi_task_with_default_config(serialization_settings: SerializationSettings):
    task_config = MPIJob(
        worker=Worker(replicas=1),
        launcher=Launcher(replicas=1),
    )
