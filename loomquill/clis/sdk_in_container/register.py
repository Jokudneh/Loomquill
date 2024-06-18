import os
import sys
import typing

import rich_click as click

from flytekit.clis.helpers import display_help_with_error
from flytekit.clis.sdk_in_container import constants
from flytekit.clis.sdk_in_container.helpers import (
    get_and_save_remote_with_click_context,
    parse_copy,
    patch_image_config,
)
from flytekit.clis.sdk_in_container.utils import domain_option_dec, project_option_dec
from flytekit.configuration import ImageConfig
from flytekit.configuration.default_images import DefaultImages
from flytekit.constants import CopyFileDetection
from flytekit.core.resources import Resources, ResourceSpec
from flytekit.interaction.click_types import key_value_callback, resource_callback
from flytekit.loggers import logger
from flytekit.tools import repo

_register_help = """
This command is similar to ``package`` but instead of producing a zip file, all your Flyte entities are compiled,
and then sent to the backend specified by your config file. Think of this as combining the ``pyflyte package``
and the ``flytectl register`` steps in one command. This is why you see switches you'd normally use with flytectl
like service account here.

Note: This command runs "fast" register by default.
This means that a zip is created from the detected root of the packages given and uploaded. Just like with
``pyflyte run``, tasks registered from this command will download and unzip that code package before running.

Note: This command only works on regular Python packages, not namespace packages. When determining
the root of your project, it finds the first folder that does not have a ``__init__.py`` file.
"""


@click.command("register", help=_register_help)
@project_option_dec
@domain_option_dec
@click.option(
    "-i",
    "--image",
    "image_config",
    required=False,
    multiple=True,
    type=click.UNPROCESSED,
    callback=ImageConfig.validate_image,
    default=[DefaultImages.default_image()],
    help="A fully qualified tag for an docker image, for example ``somedocker.com/myimage:someversion123``. This is a "
    "multi-option and can be of the form ``--image xyz.io/docker:latest"
    " --image my_image=xyz.io/docker2:latest``. Note, the ``name=image_uri``. The name is optional, if not "
    "provided the image will be used as the default image. All the names have to be unique, and thus "
    "there can only be one ``--image`` option with no name.",
)
@click.option(
