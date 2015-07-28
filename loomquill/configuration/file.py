from __future__ import annotations

import configparser
import os
import pathlib
import typing
from dataclasses import dataclass
from functools import lru_cache
from os import getenv
from pathlib import Path

import yaml

from flytekit.exceptions import user as _user_exceptions
from flytekit.loggers import logger

# This is the env var that the flytectl sandbox instructions say to set
FLYTECTL_CONFIG_ENV_VAR = "FLYTECTL_CONFIG"
# This is an explicit override only to be used by pyflyte and takes precedence in get_config_file over the main
# environment variable.
# This env var should not be set by users
FLYTECTL_CONFIG_ENV_VAR_OVERRIDE = "_FLYTECTL_CONFIG_PYFLYTE_OVERRIDE"


def _exists(val: typing.Any) -> bool:
    """Check if a value is defined."""
    return isinstance(val, bool) or bool(val is not None and val)


@dataclass
class LegacyConfigEntry(object):
    """
    Creates a record for the config entry. contains
    Args:
        section: section the option should be found under
        option: the option str to lookup
        type_: Expected type of the value
    """

    section: str
    option: str
    type_: typing.Type = str

    def get_env_name(self) -> str:
        return f"FLYTE_{self.section.upper()}_{self.option.upper()}"

    def read_from_env(self, transform: typing.Optional[typing.Callable] = None) -> typing.Optional[typing.Any]:
        """
        Reads the config entry from environment variable, the structure of the env var is current
        ``FLYTE_{SECTION}_{OPTION}`` all upper cased. We will change this in the future.
        :return:
        """
        env = self.get_env_name()
        v = os.environ.get(env, None)
        if v is None:
            return None
        return transform(v) if transform else v

    def read_from_file(
        self, cfg: ConfigFile, transform: typing.Optional[typing.Callable] = None
    ) -> typing.Optional[typing.Any]:
        if not cfg:
            return None
        try:
            v = cfg.get(self)
            return transform(v) if transform else v
        except configparser.Error:
            pass
        return None


@dataclass
class YamlConfigEntry(object):
    """
    Creates a record for the config entry.
    Args:
        switch: dot-delimited string that should match flytectl args. Leaving it as dot-delimited instead of a list
          of strings because it's easier to maintain alignment with flytectl.
        config_value_type: Expected type of the value
    """

    switch: str
    config_value_type: typing.Type = str

    def read_from_file(
        self, cfg: ConfigFile, transform: typing.Optional[typing.Callable] = None
    ) -> typing.Optional[typing.Any]:
        if not cfg:
            return None
        try:
            v = cfg.get(self)
            if _exists(v):
                return transform(v) if transform else v
        except Exception:
            ...

