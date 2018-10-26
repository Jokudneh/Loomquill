from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union

from dataclasses_json import DataClassJsonMixin
from typing_extensions import Annotated, get_args, get_origin

from flytekit import FlyteContext, lazy_module
from flytekit.core.type_engine import TypeEngine, TypeTransformer, TypeTransformerFailedError
from flytekit.models.core.types import BlobType
from flytekit.models.literals import Blob, BlobMetadata, Literal, Scalar
from flytekit.models.types import LiteralType
from flytekit.types.file import ONNXFile

sklearn = lazy_module("sklearn")
skl2onnx = lazy_module("skl2onnx")
skl2onnx_data_types = lazy_module("skl2onnx.common.data_types")


@dataclass
class ScikitLearn2ONNXConfig(DataClassJsonMixin):
    """
    ScikitLearn2ONNXConfig is the config used during the scikitlearn to ONNX conversion.

    Args:
      initial_types: The types of the inputs to the model.
      name: The name of the graph in the produced ONNX model.
      doc_string: A string attached onto the produced ONNX model.
      target_opset: The ONNX opset number.
      custom_conversion_functions: A dictionary for specifying the user customized conversion function.
      custom_shape_calculators: A dictionary for specifying the user customized shape calculator.
      custom_parsers: Parsers determine which outputs are expected for which particular task.
      options: Specific options given to converters.
      intermediate: If True, the function returns the converted model and the instance of Topology used, else, it returns the converted model.
      naming: Change the way intermediates are named.
      white_op: White list of ONNX nodes allowed while converting a pipeline.
      black_op: Black list of ONNX nodes disallowed while converting a pipeline.
      verbose: Display progress while converting a model.
