from collections import OrderedDict

import pytest
from kubernetes.client.models import V1Container, V1PodSpec

from flytekit import task
from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.core.pod_template import PodTemplate
from flytekit.core.python_auto_container import get_registerable_container_image
from flytekit.core.python_function_task import PythonFunctionTask
from flytekit.core.tracker import isnested, istestfunction
from flytekit.image_spec.image_spec import ImageBuildEngine, ImageSpec
from flytekit.tools.translator import get_serializable_task
from tests.flytekit.unit.core import tasks


def foo():
    pass


def test_isnested():
    def inner_foo():
        pass

    assert isnested(foo) is False
    assert isnested(inner_foo) is True

    # Uses tasks.tasks method
    with pytest.raises(ValueError):
        tasks.tasks()


def test_istestfunction():
    assert istestfunction(foo) is True
    assert istestfunction(isnested) is False
    assert istestfunction(tasks.tasks) is False


def test_container_image_conversion(mock_image_spec_builder):
    default_img = Image(name="default", fqn="xyz.com/abc", tag="tag1")
    other_img = Image(name="other", fqn="xyz.com/other", tag="tag-other")
    other_img2 = Image(
        name="other2",
        fqn="xyz.com/other2",
        digest="sha256:26c68657ccce2cb0a31b330cb0be2b5e108d467f641c62e13ab40cbec258c68d",
    )
    other_img3 = Image(
        name="other3",
        fqn="xyz.com/other3",
    )
    other_img4 = Image(
        name="other-4",
        fqn="other4",
        tag="tag4"
    )
    other_img5 = Image(
        name="other_5",
        fqn="xyz.com/other5",
        tag="tag5"
    )
    # Simulates _parse_image_identifier("xyz.com/other6:tag6@sha256:...") where the tag is baked into fqn
    other_img6 = Image(
        name="other6",
        fqn="xyz.com/other6:tag6",
        digest="sha256:26c68657ccce2cb0a31b330cb0be2b5e108d467f641c62e13ab40cbec258c68d",
    )
    cfg = ImageConfig(default_image=default_img, images=[default_img, other_img, other_img2, other_img3, other_img4, other_img5, other_img6])
    assert get_registerable_container_image(None, cfg) == "xyz.com/abc:tag1"
    assert get_registerable_container_image("", cfg) == "xyz.com/abc:tag1"
    assert get_registerable_container_image("abc", cfg) == "abc"
    assert get_registerable_container_image("abc:latest", cfg) == "abc:latest"
    assert get_registerable_container_image("abc:{{.image.default.version}}", cfg) == "abc:tag1"
