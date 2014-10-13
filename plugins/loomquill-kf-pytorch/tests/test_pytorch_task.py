import pytest
from flytekitplugins.kfpytorch.task import CleanPodPolicy, Master, PyTorch, RestartPolicy, RunPolicy, Worker

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


def test_pytorch_task(serialization_settings: SerializationSettings):
    @task(
        task_config=PyTorch(num_workers=10),
        cache=True,
        cache_version="1",
        requests=Resources(cpu="1"),
    )
    def my_pytorch_task(x: int, y: str) -> int:
        return x

    assert my_pytorch_task(x=10, y="hello") == 10

    assert my_pytorch_task.task_config is not None

    assert my_pytorch_task.get_custom(serialization_settings) == {
        "workerReplicas": {"replicas": 10, "resources": {}},
        "masterReplicas": {"replicas": 1, "resources": {}},
    }
    assert my_pytorch_task.resources.limits == Resources()
    assert my_pytorch_task.resources.requests == Resources(cpu="1")
    assert my_pytorch_task.task_type == "pytorch"
