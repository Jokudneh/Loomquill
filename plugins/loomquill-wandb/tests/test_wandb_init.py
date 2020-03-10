import os
from unittest.mock import Mock, patch

import pytest
from flytekitplugins.wandb import wandb_init
from flytekitplugins.wandb.tracking import WANDB_CUSTOM_TYPE_VALUE, WANDB_EXECUTION_TYPE_VALUE

from flytekit import Secret, task

secret = Secret(key="abc", group="xyz")


@pytest.mark.parametrize("id", [None, "abc123"])
def test_wandb_extra_config(id):
    wandb_decorator = wandb_init(
        project="abc",
        entity="xyz",
        secret=secret,
        id=id,
        host="https://my_org.wandb.org",
    )

    assert wandb_decorator.secret is secret
    extra_config = wandb_decorator.get_extra_config()

    if id is None:
        assert extra_config[wandb_decorator.LINK_TYPE_KEY] == WANDB_EXECUTION_TYPE_VALUE
        assert wandb_decorator.WANDB_ID_KEY not in extra_config
    else:
        assert extra_config[wandb_decorator.LINK_TYPE_KEY] == WANDB_CUSTOM_TYPE_VALUE
        assert extra_config[wandb_decorator.WANDB_ID_KEY] == id
    assert extra_config[wandb_decorator.WANDB_HOST_KEY] == "https://my_org.wandb.org"


@task
@wandb_init(project="abc", entity="xyz", secret=secret, tags=["my_tag"])
def train_model():
    pass


@patch("flytekitplugins.wandb.tracking.wandb")
def test_local_execution(wandb_mock):
    train_model()

    wandb_mock.init.assert_called_with(project="abc", entity="xyz", id=None, tags=["my_tag"])


