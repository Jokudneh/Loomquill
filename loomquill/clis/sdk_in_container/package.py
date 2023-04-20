import os
import sys
import typing

import rich_click as click

from flytekit.clis.helpers import display_help_with_error
from flytekit.clis.sdk_in_container import constants
from flytekit.clis.sdk_in_container.helpers import parse_copy
from flytekit.configuration import (
    DEFAULT_RUNTIME_PYTHON_INTERPRETER,
    FastSerializationSettings,
    ImageConfig,
    SerializationSettings,
)
from flytekit.constants import CopyFileDetection
from flytekit.interaction.click_types import key_value_callback
from flytekit.tools.fast_registration import FastPackageOptions
from flytekit.tools.repo import NoSerializableEntitiesError, serialize_and_package


@click.command("package")
@click.option(
    "-i",
    "--image",
    "image_config",
    required=False,
    multiple=True,
    type=click.UNPROCESSED,
    callback=ImageConfig.validate_image,
    help="A fully qualified tag for an docker image, for example ``somedocker.com/myimage:someversion123``. This is a "
    "multi-option and can be of the form ``--image xyz.io/docker:latest"
    " --image my_image=xyz.io/docker2:latest``. Note, the ``name=image_uri``. The name is optional, if not "
    "provided the image will be used as the default image. All the names have to be unique, and thus "
    "there can only be one ``--image`` option with no name.",
)
@click.option(
    "-s",
    "--source",
    required=False,
