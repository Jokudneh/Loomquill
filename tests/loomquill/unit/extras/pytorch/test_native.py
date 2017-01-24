import torch

from flytekit import task, workflow


@task
def generate_tensor_1d() -> torch.Tensor:
    return torch.zeros(5, dtype=torch.int32)


@task
def generate_tensor_2d() -> torch.Tensor:
    return torch.tensor([[1.0, -1.0, 2], [1.0, -1.0, 9], [0, 7.0, 3]])


@task
def generate_module() -> torch.nn.Module:
    bn = torch.nn.BatchNorm1d(3, track_running_stats=True)
