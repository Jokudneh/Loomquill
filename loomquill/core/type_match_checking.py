from __future__ import annotations

from flytekit.models.core.types import EnumType
from flytekit.models.types import LiteralType, UnionType


def literal_types_match(downstream: LiteralType, upstream: LiteralType) -> bool:
    """
    Returns if two LiteralTypes are the same.
    Takes into account arbitrary ordering of enums and unions, otherwise just an equivalence check.
    """

    # If the types are exactly the same, return True
    if downstream == upstream:
        return True

    if downstream.collection_type:
        if not upstream.collection_type:
            return False
