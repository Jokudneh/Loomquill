import re
from unittest.mock import Mock, patch

import click
import pytest

from flytekit.configuration.plugin import FlytekitPlugin, FlytekitPluginProtocol, _get_plugin_from_entrypoint


@patch("flytekit.configuration.plugin.entry_points")
def test_get_plugin_default(entry_points):
    entry_points.side_effect = lambda *args, **kwargs: []

    default_plugin = _get_plugin_from_entrypoint()
    assert default_plugin is FlytekitPlugin


@patch("flytekit.configuration.plugin.entry_points")
def test_get_plugin_errors_with_multiple_plugins(entry_points, caplog):
    entry_1 = Mock()
