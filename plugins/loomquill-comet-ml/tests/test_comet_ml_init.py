from hashlib import shake_256
from unittest.mock import patch, Mock
import pytest

from flytekit import Secret, task
from flytekitplugins.comet_ml import comet_ml_login
from flytekitplugins.comet_ml.tracking import (
    COMET_ML_CUSTOM_TYPE_VALUE,
    COMET_ML_EXECUTION_TYPE_VALUE,
    _generate_suffix_with_length_10,
    _generate_experiment_key,
)


secret = Secret(key="abc", group="xyz")


@pytest.mark.parametrize("experiment_key", [None, "abc123dfassfasfsafsafd"])
def test_extra_config(experiment_key):
    project_name = "abc"
    workspace = "my_workspace"

    comet_decorator = comet_ml_login(
        project_name=project_name,
        workspace=workspace,
        experiment_key=experiment_key,
        secret=secret
    )

    @comet_decorator
    def task():
        pass

    assert task.secret is secret
    extra_config = task.get_extra_config()

    if experiment_key is None:
        assert extra_config[task.LINK_TYPE_KEY] == COMET_ML_EXECUTION_TYPE_VALUE
        assert task.COMET_ML_EXPERIMENT_KEY_KEY not in extra_config
