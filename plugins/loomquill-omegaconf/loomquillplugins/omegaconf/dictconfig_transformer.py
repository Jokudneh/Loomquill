import importlib
import re
from typing import Any, Dict, Type, TypeVar

import flatten_dict
import flytekitplugins.omegaconf
from flyteidl.core.literals_pb2 import Literal as PB_Literal
from flytekitplugins.omegaconf.config import OmegaConfTransformerMode
from flytekitplugins.omegaconf.type_information import extract_node_type
from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.struct_pb2 import Struct

import omegaconf
from flytekit import FlyteContext
from flytekit.core.type_engine import TypeTransformerFailedError
from flytekit.extend import TypeEngine, TypeTransformer
from flytekit.loggers import logger
from flytekit.models.literals import Literal, Scalar
from flytekit.models.types import LiteralType, SimpleType
from omegaconf import DictConfig, OmegaConf

T = TypeVar("T")
NoneType = type(None)


class DictConfigTransformer(TypeTransformer[DictConfig]):
    def __init__(self):
        """Construct DictConfigTransformer."""
        super().__init__(name="OmegaConf DictConfig", t=DictConfig)

    def get_literal_type(self, t: Type[DictConfig]) -> LiteralType:
        """
        Provide type hint for Flytekit type system.

        To support the multivariate typing of nodes in a DictConfig, we encode them as binaries (no introspection)
        with multiple files.
        """
        return LiteralType(simple=SimpleType.STRUCT)

    def to_literal(self, ctx: FlyteContext, python_val: T, python_type: Type[T], expected: LiteralType) -> Literal:
        """Convert from given python type object ``DictConfig`` to the Literal representation."""
        check_if_valid_dictconfig(python_val)

        base_config = OmegaConf.get_type(python_val)
        type_map, value_map = extract_type_and_value_maps(ctx, python_val)
