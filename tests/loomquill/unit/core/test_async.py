import pytest
from flytekit.core.task import task, eager
from flytekit.core.worker_queue import Controller
from flytekit.utils.asyn import loop_manager
from flytekit.core.context_manager import FlyteContextManager
from flytekit.configuration import Config, DataConfig, S3Config, FastSerializationSettings, ImageConfig, SerializationSettings, Image
from flytekit.core.data_persistence import FileAccessProvider
from flytekit.tools.translator import get_serializable
from collections import OrderedDict

default_img = Image(name="default", fqn="test", tag="tag")
serialization_settings = SerializationSettings(
    project="project",
    domain="domain",
    version="version",
    env=None,
    image_config=ImageConfig(default_image=default_img, images=[default_img]),
)


@task
def add_one(x: int) -> int:
    return x + 1
