import pathlib
from collections import OrderedDict
from typing import Any

import pytest
from kubernetes.client.models import V1Container, V1EnvVar, V1PodSpec, V1ResourceRequirements, V1Volume

from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.core.base_task import TaskMetadata
from flytekit.core.pod_template import PodTemplate
from flytekit.core.python_auto_container import PythonAutoContainerTask, get_registerable_container_image, default_notebook_task_resolver
from flytekit.core.resources import Resources
from flytekit.image_spec.image_spec import ImageBuildEngine, ImageSpec
from flytekit.tools.translator import get_serializable_task, Options


@pytest.fixture
def default_image_config():
    default_image = Image(name="default", fqn="docker.io/xyz", tag="some-git-hash")
    return ImageConfig(default_image=default_image)


@pytest.fixture
def no_default_image_config():
    other_image = Image(name="other", fqn="docker.io/xyz", tag="some-git-hash")
    return ImageConfig.create_from(default_image=None, other_images=[other_image])


@pytest.fixture
def default_serialization_settings(default_image_config):
    return SerializationSettings(
        project="p", domain="d", version="v", image_config=default_image_config, env={"FOO": "bar"}
    )


@pytest.fixture
def minimal_serialization_settings(default_image_config):
    return SerializationSettings(project="p", domain="d", version="v", image_config=default_image_config)


@pytest.fixture
def minimal_serialization_settings_no_default_image(no_default_image_config):
    return SerializationSettings(project="p", domain="d", version="v", image_config=no_default_image_config)


@pytest.fixture(
    params=[
        "default_serialization_settings",
        "minimal_serialization_settings",
        "minimal_serialization_settings_no_default_image",
    ],
    scope="function",
)
def serialization_settings(request):
    return request.getfixturevalue(request.param)


def test_image_name_interpolation(default_image_config):
    image_spec = ImageSpec(name="image-1", registry="localhost:30000", builder="test")

    new_img_cfg = ImageConfig.create_from(
        default_image_config.default_image,
        other_images=[Image.look_up_image_info(image_spec.id, "flyte/test:d1")],
    )
    img_to_interpolate = "{{.image.default.fqn}}:{{.image.default.version}}-special"
    img = get_registerable_container_image(img=img_to_interpolate, cfg=new_img_cfg)
    assert img == "docker.io/xyz:some-git-hash-special"
    img = get_registerable_container_image(img=image_spec, cfg=new_img_cfg)
    assert img == "flyte/test:d1"


class DummyAutoContainerTask(PythonAutoContainerTask):
    def execute(self, **kwargs) -> Any:
        pass


task = DummyAutoContainerTask(name="x", task_config=None, task_type="t")


def test_default_command(default_serialization_settings):
    cmd = task.get_default_command(settings=default_serialization_settings)
    assert cmd == [
        "pyflyte-execute",
        "--inputs",
        "{{.input}}",
        "--output-prefix",
        "{{.outputPrefix}}",
        "--raw-output-data-prefix",
        "{{.rawOutputDataPrefix}}",
        "--checkpoint-path",
        "{{.checkpointOutputPrefix}}",
        "--prev-checkpoint",
        "{{.prevCheckpointPrefix}}",
        "--resolver",
        "flytekit.core.python_auto_container.default_task_resolver",
        "--",
        "task-module",
        "tests.flytekit.unit.core.test_python_auto_container",
        "task-name",
        "task",
    ]



def test_get_container(default_serialization_settings):
    c = task.get_container(default_serialization_settings)
    assert c.image == "docker.io/xyz:some-git-hash"
    assert c.env == {"FOO": "bar"}

