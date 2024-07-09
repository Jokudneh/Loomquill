import uuid

import pytest

from flytekit.configuration import Config, ImageConfig, SerializationSettings
from flytekit.loggers import logger
from flytekit.remote.remote import FlyteRemote

from .resources import hello_wf

#####
# THESE TESTS ARE NOT RUN IN CI. THEY ARE HERE TO MAKE LOCAL TESTING EASIER.
# Update these to use these tests
IMAGE_STR = "flytecookbook:core-f7af27e23b3935a166645cf96a68583cdd263a87"
FETCH_VERSION = "a351b7c7445a8a818cdf87bf1c1cf38b63beddf1"
RELEASED_EXAMPLES_VERSION = "a351b7c7445a8a818cdf87bf1c1cf38b63beddf1"
#####

image_config = ImageConfig.auto(img_name=IMAGE_STR)

rr = FlyteRemote(
    Config.for_sandbox(),
    default_project="flytesnacks",
    default_domain="development",
)


def get_get_version():
    _VERSION_PREFIX = "sandbox_test_" + uuid.uuid4().hex[:3]
    logger.warning(f"Test version prefix is {_VERSION_PREFIX}")
    print(f"fdsafdsaTest version prefix is {_VERSION_PREFIX}")

    def fn(suffix: str = "") -> str:
        return _VERSION_PREFIX + (f"_{suffix}" if suffix else "")

    return fn


get_version = get_get_version()
