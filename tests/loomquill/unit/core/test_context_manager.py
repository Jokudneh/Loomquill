import base64
import os
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock

import mock
import py
import pytest

import flytekit.configuration.plugin
from flytekit.configuration import (
    SERIALIZED_CONTEXT_ENV_VAR,
    FastSerializationSettings,
    Image,
    ImageConfig,
    SecretsConfig,
    SerializationSettings,
)
from flytekit.core import mock_stats, context_manager
from flytekit.core.context_manager import ExecutionParameters, FlyteContext, FlyteContextManager, SecretsManager
from flytekit.core.resources import ResourceSpec, Resources
from flytekit.models.core import identifier as id_models


class SampleTestClass(object):
    def __init__(self, value):
        self.value = value


def test_levels():
    ctx = FlyteContextManager.current_context()
    b = ctx.new_builder()
    b.flyte_client = SampleTestClass(value=1)
    with FlyteContextManager.with_context(b) as outer:
        assert outer.flyte_client.value == 1
        b = outer.new_builder()
        b.flyte_client = SampleTestClass(value=2)
        with FlyteContextManager.with_context(b) as ctx:
            assert ctx.flyte_client.value == 2

        with FlyteContextManager.with_context(outer.with_new_compilation_state()) as ctx:
            assert ctx.flyte_client.value == 1


def test_default():
    ctx = FlyteContext.current_context()
    assert ctx.file_access is not None


def test_look_up_image_info():
    img = Image.look_up_image_info(name="x", image_identifier="docker.io/xyz", allow_no_tag_or_digest=True)
    assert img.name == "x"
    assert img.tag is None
    assert img.digest is None
    assert img.fqn == "docker.io/xyz"

    with pytest.raises(AssertionError):
        Image.look_up_image_info(name="x", image_identifier="docker.io/xyz", allow_no_tag_or_digest=False)

