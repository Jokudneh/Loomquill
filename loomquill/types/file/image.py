import pathlib
import typing
from typing import Type

import PIL.Image

from flytekit.core.context_manager import FlyteContext
from flytekit.core.type_engine import TypeEngine, TypeTransformer, TypeTransformerFailedError
from flytekit.models.core import types as _core_types
from flytekit.models.literals import Blob, BlobMetadata, Literal, Scalar
from flytekit.models.types import LiteralType

T = typing.TypeVar("T")


class PILImageTransformer(TypeTransformer[T]):
    """
    TypeTransformer that supports PIL.Image as a native type.
    """

    FILE_FORMAT = "PIL.Image"

    def __init__(self):
