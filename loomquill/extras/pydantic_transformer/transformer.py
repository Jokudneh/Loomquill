import json
import os
from typing import Type

import msgpack
from google.protobuf import json_format as _json_format
from google.protobuf import struct_pb2 as _struct
from pydantic import BaseModel

from flytekit import FlyteContext
from flytekit.core.constants import CACHE_KEY_METADATA, FLYTE_USE_OLD_DC_FORMAT, MESSAGEPACK, SERIALIZATION_FORMAT
from flytekit.core.type_engine import TypeEngine, TypeTransformer, TypeTransformerFailedError
from flytekit.core.utils import str2bool
from flytekit.loggers import logger
from flytekit.models import types
from flytekit.models.annotation import TypeAnnotation as TypeAnnotationModel
from flytekit.models.literals import Binary, Literal, Scalar
from flytekit.models.types import LiteralType, TypeStructure


class PydanticTransformer(TypeTransformer[BaseModel]):
    def __init__(self):
        super().__init__("Pydantic Transformer", BaseModel, enable_type_assertions=False)

    def get_literal_type(self, t: Type[BaseModel]) -> LiteralType:
        schema = t.model_json_schema()
        literal_type = {}

        for name, field_info in t.model_fields.items():
            python_type = field_info.annotation
            try:
                literal_type[name] = TypeEngine.to_literal_type(python_type)
            except Exception as e:
                logger.warning(
                    "Field {} of type {} cannot be converted to a literal type. Error: {}".format(name, python_type, e)
                )

        # This is for attribute access in FlytePropeller.
        ts = TypeStructure(tag="", dataclass_type=literal_type)

