import datetime
import json

import pytest
from google.protobuf.json_format import Parse
from google.protobuf.struct_pb2 import Struct

from flytekit import BlobType
from flytekit.interaction.string_literals import (
    literal_map_string_repr,
    literal_string_repr,
    primitive_to_string,
    scalar_to_string,
)
from flytekit.models.literals import (
    Binary,
    Blob,
    BlobMetadata,
    Literal,
    LiteralCollection,
    LiteralMap,
    Primitive,
    Scalar,
    StructuredDataset,
    Schema,
    Union,
    Void,
)
from flytekit.models.types import Error, LiteralType, SimpleType, SchemaType


