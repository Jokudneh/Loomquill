import os
import typing
from dataclasses import dataclass
from unittest import mock
from typing_extensions import Annotated, cast
from flytekitplugins.kfpytorch.task import Elastic

from flytekit import Artifact

import pytest
import torch
import torch.distributed as dist
from dataclasses_json import DataClassJsonMixin
from flytekitplugins.kfpytorch.task import CleanPodPolicy, Elastic, RunPolicy

import flytekit
from flytekit import task, workflow
from flytekit.core.context_manager import FlyteContext, FlyteContextManager, ExecutionState, ExecutionParameters, OutputMetadataTracker
from flytekit.configuration import SerializationSettings
from flytekit.exceptions.user import FlyteRecoverableException, FlyteUserRuntimeException

@pytest.fixture(autouse=True, scope="function")
def restore_env():
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)

@dataclass
class Config(DataClassJsonMixin):
    lr: float = 1e-5
    bs: int = 64
    name: str = "foo"


def dist_communicate() -> int:
    """Communicate between distributed workers."""
    rank = torch.distributed.get_rank()
    world_size = dist.get_world_size()
    tensor = torch.tensor([5], dtype=torch.int64) + 2 * rank + world_size
    dist.all_reduce(tensor, op=dist.ReduceOp.SUM)

    return tensor.item()


def train(config: Config) -> typing.Tuple[str, Config, torch.nn.Module, int]:
    """Mock training a model using torch-elastic for test purposes."""
    dist.init_process_group(backend="gloo")

    local_rank = os.environ["LOCAL_RANK"]

    out_model = torch.nn.Linear(1000, int(local_rank) + 1)
    config.name = "elastic-test"

    distributed_result = dist_communicate()

    return f"result from local rank {local_rank}", config, out_model, distributed_result


@pytest.mark.parametrize("start_method", ["spawn", "fork"])
def test_end_to_end(start_method: str) -> None:
    """Test that the workflow with elastic task runs end to end."""
    world_size = 2

    train_task = task(train,task_config=Elastic(nnodes=1, nproc_per_node=world_size, start_method=start_method))

    @workflow
    def wf(config: Config = Config()) -> typing.Tuple[str, Config, torch.nn.Module, int]:
        return train_task(config=config)

    r, cfg, m, distributed_result = wf()
    assert "result from local rank 0" in r
    assert cfg.name == "elastic-test"
    assert m.in_features == 1000
    assert m.out_features == 1
    """
    The distributed result is calculated by the workers of the elastic train
    task by performing a `dist.all_reduce` operation. The correct result can
    only be obtained if the distributed process group is initialized correctly.
    """
    assert distributed_result == sum([5 + 2 * rank + world_size for rank in range(world_size)])


@pytest.mark.parametrize(
    "start_method,target_exec_id,monkeypatch_exec_id_env_var",
    [
        ("spawn", "", False),
        ("spawn", "f12345678", True),
        ("fork", "local", False),
    ],
)
def test_execution_params(start_method: str, target_exec_id: str, monkeypatch_exec_id_env_var: bool, monkeypatch) -> None:
    """Test that execution parameters are set in the worker processes."""
    if monkeypatch_exec_id_env_var:
        monkeypatch.setenv("FLYTE_INTERNAL_EXECUTION_ID", target_exec_id)

