from collections import OrderedDict
from datetime import timedelta

from flytekitplugins.sleep import Sleep
from flytekitplugins.sleep.task import SleepFunctionTask

from flytekit import task, workflow
from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.extend import get_serializable

default_img = Image(name="default", fqn="test", tag="tag")
serialization_settings = SerializationSettings(
    project="proj",
    domain="dom",
    version="123",
    image_config=ImageConfig(default_image=default_img, images=[default_img]),
