from collections import OrderedDict
from functools import partial

import numpy as np
import pytest
from sklearn.base import BaseEstimator
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVC

import flytekit
from flytekit import task
from flytekit.configuration import Image, ImageConfig
from flytekit.core import context_manager
from flytekit.extras.sklearn import SklearnEstimatorTransformer
from flytekit.models.core.types import BlobType
from flytekit.models.literals import BlobMetadata
from flytekit.models.types import LiteralType
from flytekit.tools.translator import get_serializable

default_img = Image(name="default", fqn="test", tag="tag")
serialization_settings = flytekit.configuration.SerializationSettings(
    project="project",
    domain="domain",
    version="version",
    env=None,
    image_config=ImageConfig(default_image=default_img, images=[default_img]),
)


