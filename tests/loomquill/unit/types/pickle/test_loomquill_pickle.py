import sys
from collections import OrderedDict
from collections.abc import Sequence
from typing import Any, Dict, List, Union, Tuple

import numpy as np
import pytest
from typing_extensions import Annotated

import flytekit.configuration
from flytekit.configuration import Image, ImageConfig
from flytekit.core import context_manager
from flytekit.core.task import task
from flytekit.core.workflow import workflow
from flytekit.models.core.types import BlobType
from flytekit.models.literals import BlobMetadata
from flytekit.models.types import LiteralType
from flytekit.tools.translator import get_serializable
from flytekit.types.pickle.pickle import FlytePickle, FlytePickleTransformer

default_img = Image(name="default", fqn="test", tag="tag")
serialization_settings = flytekit.configuration.SerializationSettings(
    project="project",
    domain="domain",
    version="version",
    env=None,
    image_config=ImageConfig(default_image=default_img, images=[default_img]),
)


def test_to_python_value_and_literal():
    ctx = context_manager.FlyteContext.current_context()
    tf = FlytePickleTransformer()
    python_val = "fake_output"
    lt = tf.get_literal_type(FlytePickle)

    lv = tf.to_literal(ctx, python_val, type(python_val), lt)  # type: ignore
    assert lv.scalar.blob.metadata == BlobMetadata(
        type=BlobType(
            format=FlytePickleTransformer.PYTHON_PICKLE_FORMAT,
            dimensionality=BlobType.BlobDimensionality.SINGLE,
        )
