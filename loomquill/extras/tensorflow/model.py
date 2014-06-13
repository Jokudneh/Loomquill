import pathlib
from typing import Type

import tensorflow as tf

from flytekit.core.context_manager import FlyteContext
from flytekit.core.type_engine import AsyncTypeTransformer, TypeEngine, TypeTransformerFailedError
from flytekit.models.core import types as _core_types
from flytekit.models.literals import Blob, BlobMetadata, Literal, Scalar
from flytekit.models.types import LiteralType


class TensorFlowModelTransformer(AsyncTypeTransformer[tf.keras.Model]):
    TENSORFLOW_FORMAT = "TensorFlowModel"

