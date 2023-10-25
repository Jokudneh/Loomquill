import os

import pytest

import flytekit.configuration.plugin
from flytekit.configuration.plugin import FlytekitPlugin


@pytest.fixture(autouse=True, scope="session")
def configure_plugin():
    """If a plugin is installed then the global plugin refers to an external plugin.
