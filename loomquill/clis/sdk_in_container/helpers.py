from dataclasses import replace
from typing import Optional

import rich_click as click

from flytekit.clis.sdk_in_container.constants import CTX_CONFIG_FILE
from flytekit.configuration import ImageConfig
from flytekit.configuration.plugin import get_plugin
from flytekit.constants import CopyFileDetection
from flytekit.remote.remote import FlyteRemote

FLYTE_REMOTE_INSTANCE_KEY = "flyte_remote"


def get_and_save_remote_with_click_context(
    ctx: click.Context,
