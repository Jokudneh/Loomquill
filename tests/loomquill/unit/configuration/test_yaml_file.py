import os

import mock
from unittest.mock import patch
from flytekit.configuration import ConfigEntry, get_config_file
from flytekit.configuration.file import LegacyConfigEntry, YamlConfigEntry
from flytekit.configuration.internal import AWS, Credentials, Images, Platform


def test_config_entry_file():
    c = ConfigEntry(
        LegacyConfigEntry("platform", "url", str), YamlConfigEntry("admin.endpoint"), lambda x: x.replace("dns:///", "")
    )
    assert c.read() is None

    cfg = get_config_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), "configs/sample.yaml"))
    assert cfg.yaml_config is not None
    assert c.read(cfg) == "flyte.mycorp.io"

    c = ConfigEntry(LegacyConfigEntry("platform", "url2", str))  # Does not exist
    assert c.read(cfg) is None


def test_config_entry_file_normal():
