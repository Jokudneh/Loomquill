import base64
import json
import typing

import msgpack
from google.protobuf.json_format import MessageToDict

from flytekit.models.literals import Literal, LiteralMap, Primitive, Scalar


def primitive_to_string(primitive: Primitive) -> typing.Any:
    """
    This method is used to convert a primitive to a string representation.
    """
    if primitive.integer is not None:
        return primitive.integer
    if primitive.float_value is not None:
        return primitive.float_value
    if primitive.boolean is not None:
        return primitive.boolean
    if primitive.string_value is not None:
        return primitive.string_value
    if primitive.datetime is not None:
