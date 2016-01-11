import pytest
from flytekitplugins.kftensorflow import PS, Chief, CleanPodPolicy, Evaluator, RestartPolicy, RunPolicy, TfJob, Worker

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


def test_tensorflow_task_with_default_config(serialization_settings: SerializationSettings):
    task_config = TfJob(
        worker=Worker(replicas=1),
        chief=Chief(replicas=0),
        ps=PS(replicas=0),
        evaluator=Evaluator(replicas=0),
    )

    @task(
        task_config=task_config,
        cache=True,
        requests=Resources(cpu="1"),
        cache_version="1",
    )
    def my_tensorflow_task(x: int, y: str) -> int:
        return x

    assert my_tensorflow_task(x=10, y="hello") == 10

    assert my_tensorflow_task.task_config is not None
    assert my_tensorflow_task.task_type == "tensorflow"
    assert my_tensorflow_task.resources.limits == Resources()
    assert my_tensorflow_task.resources.requests == Resources(cpu="1")

    expected_dict = {
        "chiefReplicas": {
            "resources": {},
