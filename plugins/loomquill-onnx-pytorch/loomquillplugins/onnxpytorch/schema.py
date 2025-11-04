from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Type, Union

from dataclasses_json import DataClassJsonMixin
from typing_extensions import Annotated, get_args, get_origin

from flytekit import FlyteContext, lazy_module
from flytekit.core.type_engine import TypeEngine, TypeTransformer, TypeTransformerFailedError
from flytekit.models.core.types import BlobType
from flytekit.models.literals import Blob, BlobMetadata, Literal, Scalar
from flytekit.models.types import LiteralType
from flytekit.types.file import ONNXFile

torch = lazy_module("torch")


@dataclass
class PyTorch2ONNXConfig(DataClassJsonMixin):
    """
    PyTorch2ONNXConfig is the config used during the pytorch to ONNX conversion.

    Args:
      args: The input to the model.
      export_params: Whether to export all the parameters.
      verbose: Whether to print description of the ONNX model.
      training: Whether to export the model in training mode or inference mode.
      opset_version: The ONNX version to export the model to.
      input_names: Names to assign to the input nodes of the graph.
      output_names: Names to assign to the output nodes of the graph.
      operator_export_type: How to export the ops.
      do_constant_folding: Whether to apply constant folding for optimization.
      dynamic_axes: Specify axes of tensors as dynamic.
      keep_initializers_as_inputs: Whether to add the initializers as inputs to the graph.
      custom_opsets: A dictionary of opset domain name and version.
      export_modules_as_functions: Whether to export modules as functions.
    """
