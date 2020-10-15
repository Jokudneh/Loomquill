from typing import Union
import math

import asyncio
from typing import Union
import optuna

import flytekit as fl
from flytekitplugins.optuna import optimize, suggest


def test_local_exec():

    @fl.eager
    async def train(concurrency: int, n_trials: int) -> float:

        @optimize(concurrency=concurrency, n_trials=n_trials)
        @fl.task
        async def optimizer(x: float, y: int, z: int, power: int) -> float:
            return (((x - 5) ** 2) + (y + 4) ** 4 + (3 * z - 3) ** 2) ** power

        await optimizer(
            x=suggest.float(low=-10, high=10),
            y=suggest.integer(low=-10, high=10),
            z=suggest.category([-5, 0, 3, 6, 9]),
