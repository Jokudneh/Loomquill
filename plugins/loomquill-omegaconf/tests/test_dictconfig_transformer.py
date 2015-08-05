import typing as t

import pytest
from flytekitplugins.omegaconf.dictconfig_transformer import (
    check_if_valid_dictconfig,
    extract_type_and_value_maps,
    is_flattenable,
    parse_type_description, NoneType,
)
from omegaconf import DictConfig, OmegaConf

from flytekit import FlyteContext


@pytest.mark.parametrize(
    "config, should_raise, match",
    [
        (OmegaConf.create({"key1": "value1", "key2": 123, "key3": True}), False, None),
        ({"key1": "value1"}, True, "Invalid type <class 'dict'>, can only serialize DictConfigs"),
        (
            OmegaConf.create({"key1.with.dot": "value1", "key2": 123}),
            True,
            "cannot be flattened as it contains non-string keys or keys containing dots",
        ),
        (
            OmegaConf.create({1: "value1", "key2": 123}),
            True,
