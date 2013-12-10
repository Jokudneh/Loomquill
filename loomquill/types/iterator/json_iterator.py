from pathlib import Path
from typing import Any, Dict, Iterator, List, Type, Union

import jsonlines
from typing_extensions import TypeAlias

from flytekit import FlyteContext, Literal, LiteralType
from flytekit.core.type_engine import (
    AsyncTypeTransformer,
    TypeEngine,
    TypeTransformerFailedError,
)
from flytekit.models.core import types as _core_types
from flytekit.models.literals import Blob, BlobMetadata, Scalar

JSONCollection: TypeAlias = Union[Dict[str, Any], List[Any]]
JSONScalar: TypeAlias = Union[bool, float, int, str]
JSON: TypeAlias = Union[JSONCollection, JSONScalar]


class JSONIterator(Iterator[JSON]):
    def __init__(self, reader: jsonlines.Reader):
        self._reader = reader
        self._reader_iter = reader.iter()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self._reader_iter)
        except StopIteration:
            self._reader.close()
            raise StopIteration("File handler is exhausted")


