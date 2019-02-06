from typing import List, NamedTuple

import numpy
import onnxruntime as rt
import pandas as pd
from flytekitplugins.onnxscikitlearn import ScikitLearn2ONNX, ScikitLearn2ONNXConfig
from skl2onnx.common._apply_operation import apply_mul
from skl2onnx.common.data_types import FloatTensorType
from skl2onnx.proto import onnx_proto
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from typing_extensions import Annotated

from flytekit import task, workflow
from flytekit.types.file import ONNXFile


def test_onnx_scikitlearn_simple():
    TrainOutput = NamedTuple(
        "TrainOutput",
        [
            (
                "model",
                Annotated[
                    ScikitLearn2ONNX,
                    ScikitLearn2ONNXConfig(
                        initial_types=[("float_input", FloatTensorType([None, 4]))],
                        target_opset=12,
                    ),
                ],
            ),
            ("test", pd.DataFrame),
