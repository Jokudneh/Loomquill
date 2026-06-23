from typing import TYPE_CHECKING, Optional, Tuple

from flyteidl.core.literals_pb2 import LiteralMap

from flytekit import lazy_module
from flytekit.models.literals import Literal, LiteralCollection
from flytekit.models.literals import LiteralMap as ModelLiteralMap

if TYPE_CHECKING:
    from diskcache import Cache

joblib = lazy_module("joblib")

# Location on the filesystem where serialized objects will be stored
# TODO: read from config
CACHE_LOCATION = "~/.flyte/local-cache"


def _recursive_hash_placement(literal: Literal) -> Literal:
    # Base case, hash gets passed through always if set
    if literal.hash is not None:
        return Literal(hash=literal.hash)
    elif literal.collection is not None:
        literals = [_recursive_hash_placement(lit) for lit in literal.collection.literals]
        return Literal(collection=LiteralCollection(literals=literals))
    elif literal.map is not None:
        literal_map = {}
        for key, literal_value in literal.map.literals.items():
            literal_map[key] = _recursive_hash_placement(literal_value)
        return Literal(map=ModelLiteralMap(literal_map))
    else:
        return literal


def _calculate_cache_key(
    task_name: str,
    cache_version: str,
    input_literal_map: ModelLiteralMap,
