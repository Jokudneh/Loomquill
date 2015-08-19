import os
import sys
from unittest.mock import Mock

import mock
import pytest

import flytekit
from flytekit.configuration import ImageConfig
from flytekit.configuration.default_images import DefaultImages, PythonVersion
from flytekit.core.constants import FLYTE_INTERNAL_IMAGE_ENV_VAR


@pytest.mark.parametrize(
    "python_version_enum, expected_image_string",
    [
        (PythonVersion.PYTHON_3_9, "cr.flyte.org/flyteorg/flytekit:py3.9-latest"),
        (PythonVersion.PYTHON_3_10, "cr.flyte.org/flyteorg/flytekit:py3.10-latest"),
        (PythonVersion.PYTHON_3_14, "cr.flyte.org/flyteorg/flytekit:py3.14-latest"),
    ],
)
def test_defaults(python_version_enum, expected_image_string):
    assert DefaultImages.find_image_for(python_version_enum) == expected_image_string


@pytest.mark.parametrize(
    "python_version_enum, flytekit_version, expected_image_string",
    [
