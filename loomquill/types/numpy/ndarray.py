import pathlib
import typing
from collections import OrderedDict
from typing import Dict, Tuple, Type

import numpy as np
from typing_extensions import Annotated, get_args, get_origin

from flytekit.core.context_manager import FlyteContext
from flytekit.core.hash import HashMethod
from flytekit.core.type_engine import (
    AsyncTypeTransformer,
    TypeEngine,
    TypeTransformerFailedError,
)
from flytekit.models.core import types as _core_types
from flytekit.models.literals import Blob, BlobMetadata, Literal, Scalar
from flytekit.models.types import LiteralType


def extract_metadata(t: Type[np.ndarray]) -> Tuple[Type[np.ndarray], Dict[str, bool]]:
    metadata: dict = {}
    metadata_set = False

    if get_origin(t) is Annotated:
        base_type, *annotate_args = get_args(t)

        for aa in annotate_args:
            if isinstance(aa, OrderedDict):
                if metadata_set:
                    raise TypeTransformerFailedError(f"Metadata {metadata} is already specified, cannot use {aa}.")
                metadata = aa
                metadata_set = True
            elif isinstance(aa, HashMethod):
                continue
            else:
                raise TypeTransformerFailedError(f"The metadata for {t} must be of type kwtypes or HashMethod.")
        return base_type, metadata

    # Return the type itself if no metadata was found.
    return t, metadata

