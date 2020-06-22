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
        super().__init__(name="PIL.Image", t=PIL.Image.Image)

    def get_literal_type(self, t: Type[T]) -> LiteralType:
        return LiteralType(
            blob=_core_types.BlobType(
                format=self.FILE_FORMAT, dimensionality=_core_types.BlobType.BlobDimensionality.SINGLE
