from collections import OrderedDict

from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.core.task import task
from flytekit.extras.accelerators import A100, T4
from flytekit.tools.translator import get_serializable

serialization_settings = SerializationSettings(
    project="proj",
    domain="dom",
    version="123",
    image_config=ImageConfig(Image(name="name", fqn="asdf/fdsa", tag="123")),
    env={},
)


