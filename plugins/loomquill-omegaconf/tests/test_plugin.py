from typing import Any

import flytekitplugins.omegaconf
import pytest
from flyteidl.core.literals_pb2 import Literal, Scalar
from flytekitplugins.omegaconf.config import OmegaConfTransformerMode
from flytekitplugins.omegaconf.dictconfig_transformer import DictConfigTransformer
from google.protobuf.struct_pb2 import Struct
from omegaconf import MISSING, DictConfig, ListConfig, OmegaConf, ValidationError
from pytest import mark, param

from flytekit import FlyteContext
from flytekit.core.type_engine import TypeEngine
from tests.conftest import ExampleConfig, ExampleNestedConfig
from tests.test_objects import TEST_CFG, MultiTypeEnum, MyConf, MySubConf, SpecialConf


@mark.parametrize(
    ("obj"),
    [
        param(
            DictConfig({}),
        ),
        param(
            DictConfig({"a": "b"}),
        ),
        param(
            DictConfig({"a": 1}),
        ),
        param(
            DictConfig({"a": MISSING}),
        ),
        param(
            DictConfig({"tuple": (1, 2, 3)}),
        ),
        param(
            ListConfig(["a", "b"]),
        ),
        param(
            ListConfig(["a", MISSING]),
        ),
        param(
            TEST_CFG,
        ),
        param(
            OmegaConf.create(ExampleNestedConfig()),
        ),
        param(
            OmegaConf.create(ExampleConfig()),
        ),
        param(
            DictConfig({"foo": MultiTypeEnum.fifo}),
        ),
        param(
            DictConfig({"foo": [MultiTypeEnum.fifo]}),
        ),
        param(DictConfig({"cfgs": [MySubConf(1), MySubConf("a"), "arg"]})),
        param(OmegaConf.structured(SpecialConf)),
