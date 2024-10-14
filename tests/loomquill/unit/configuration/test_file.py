import configparser
import datetime
import os

import mock
import pytest
from pathlib import Path
from pytimeparse.timeparse import timeparse

from flytekit.configuration import ConfigEntry, get_config_file, set_if_exists, Config
from flytekit.configuration.file import LegacyConfigEntry, _exists, FLYTECTL_CONFIG_ENV_VAR, FLYTECTL_CONFIG_ENV_VAR_OVERRIDE
from flytekit.configuration.internal import Platform


def test_set_if_exists():
    d = {}
    d = set_if_exists(d, "k", None)
    assert len(d) == 0
    d = set_if_exists(d, "k", [])
    assert len(d) == 0
    d = set_if_exists(d, "k", "x")
    assert len(d) == 1
    assert d["k"] == "x"


@pytest.mark.parametrize(
    "data, expected",
    [
        [1, True],
        [1.0, True],
        ["foo", True],
        [True, True],
        [False, True],
        [[1], True],
        [{"k": "v"}, True],
        [None, False],
        [[], False],
        [{}, False],
    ],
)
def test_exists(data, expected):
    assert _exists(data) is expected


def test_get_config_file():
