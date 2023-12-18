from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from dataclasses_json import DataClassJsonMixin
from typing_extensions import Annotated, get_args, get_origin

from flytekit import FlyteContext, lazy_module
from flytekit.core.type_engine import TypeEngine, TypeTransformer, TypeTransformerFailedError
from flytekit.models.core.types import BlobType
from flytekit.models.literals import Blob, BlobMetadata, Literal, Scalar
from flytekit.models.types import LiteralType
from flytekit.types.file import ONNXFile

np = lazy_module("numpy")
tf = lazy_module("tensorflow")
tf2onnx = lazy_module("tf2onnx")


@dataclass
class TensorFlow2ONNXConfig(DataClassJsonMixin):
    """
    TensorFlow2ONNXConfig is the config used during the tensorflow to ONNX conversion.

    Args:
      input_signature: The shape/dtype of the inputs to the model.
      custom_ops: If a model contains ops not recognized by ONNX runtime, you can tag these ops with a custom op domain so that the runtime can still open the model.
      target: List of workarounds applied to help certain platforms.
      custom_op_handlers: A dictionary of custom op handlers.
      custom_rewriter: A list of custom graph rewriters.
      opset: The ONNX opset number.
      extra_opset: The extra ONNX opset numbers to be used by, say, custom ops.
