import flytekit as fl
import pytest

from flytekitplugins.optuna import Optimizer


@fl.task
async def objective(x: float, y: int, z: int, power: int) -> float:
    return 1.0

def test_concurrency():

    with pytest.raises(ValueError):
        Optimizer(objective, concurrency=-1, n_trials=10)

    with pytest.raises(ValueError):
        Optimizer(objective, concurrency=0, n_trials=10)

    with pytest.raises(ValueError):
        Optimizer(objective, concurrency="abc", n_trials=10)


def test_n_trials():

    with pytest.raises(ValueError):
        Optimizer(objective, concurrency=3, n_trials=-10)

    with pytest.raises(ValueError):
