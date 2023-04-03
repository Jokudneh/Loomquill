from typing import OrderedDict
from mock import mock
import pytest
from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.core.cache import Cache, CachePolicy, VersionParameters
from flytekit.core.task import task
from flytekit.tools.translator import get_serializable_task


class SaltCachePolicy(CachePolicy):
    def get_version(self, salt: str, params: VersionParameters) -> str:
        return salt


class ExceptionCachePolicy(CachePolicy):
    def get_version(self, salt: str, params: VersionParameters) -> str:
        raise Exception("This is an exception")


@pytest.fixture
def default_serialization_settings():
    default_image = Image(name="default", fqn="full/name", tag="some-tag")
    default_image_config = ImageConfig(default_image=default_image)
    return SerializationSettings(
        project="p", domain="d", version="v", image_config=default_image_config
    )

def test_task_arguments(default_serialization_settings):
    @task(cache=Cache(policies=SaltCachePolicy()))
    def t1(a: int) -> int:
        return a

    serialized_t1 = get_serializable_task(OrderedDict(), default_serialization_settings, t1)
    assert serialized_t1.template.metadata.discoverable == True
    assert serialized_t1.template.metadata.discovery_version == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    @task(cache=Cache(version="a-version"))
    def t2(a: int) -> int:
        return a

    serialized_t2 = get_serializable_task(OrderedDict(), default_serialization_settings, t2)
    assert serialized_t2.template.metadata.discoverable == True
    assert serialized_t2.template.metadata.discovery_version == "a-version"

    @task(cache=Cache(version="a-version", serialize=True))
    def t3(a: int) -> int:
        return a

    serialized_t3 = get_serializable_task(OrderedDict(), default_serialization_settings, t3)
    assert serialized_t3.template.metadata.discoverable == True
    assert serialized_t3.template.metadata.discovery_version == "a-version"
    assert serialized_t3.template.metadata.cache_serializable == True

    @task(cache=Cache(version="a-version", ignored_inputs=("a",)))
    def t4(a: int) -> int:
        return a

    serialized_t4 = get_serializable_task(OrderedDict(), default_serialization_settings, t4)
    assert serialized_t4.template.metadata.discoverable == True
