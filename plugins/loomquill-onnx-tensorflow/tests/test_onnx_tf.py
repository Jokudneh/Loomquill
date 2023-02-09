import urllib
from io import BytesIO
from typing import List, NamedTuple

import numpy as np
import onnxruntime as rt
import tensorflow as tf
from flytekitplugins.onnxtensorflow import TensorFlow2ONNX, TensorFlow2ONNXConfig
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image
from typing_extensions import Annotated

from flytekit import task, workflow
from flytekit.types.file import ONNXFile


def test_tf_onnx():
    @task
    def load_test_img() -> np.ndarray:
        with urllib.request.urlopen(
            "https://raw.githubusercontent.com/flyteorg/static-resources/main/flytekit/onnx/ade20k.jpg"
        ) as url:
            img = image.load_img(
                BytesIO(url.read()),
                target_size=(224, 224),
            )

        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
