import importlib
from typing import Type, TypeVar

from flyteidl.core.literals_pb2 import Literal as PB_Literal
from flytekitplugins.omegaconf.type_information import extract_node_type
from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.struct_pb2 import Struct

import omegaconf
from flytekit import FlyteContext
from flytekit.core.type_engine import TypeTransformerFailedError
from flytekit.extend import TypeEngine, TypeTransformer
from flytekit.models.literals import Literal, Primitive, Scalar
from flytekit.models.types import LiteralType, SimpleType
from omegaconf import ListConfig, OmegaConf

T = TypeVar("T")


class ListConfigTransformer(TypeTransformer[ListConfig]):
    def __init__(self):
        """Construct ListConfigTransformer."""
        super().__init__(name="OmegaConf ListConfig", t=ListConfig)

    def get_literal_type(self, t: Type[ListConfig]) -> LiteralType:
        """
        Provide type hint for Flytekit type system.

