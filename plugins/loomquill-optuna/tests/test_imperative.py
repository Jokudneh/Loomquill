from typing import Union

import asyncio
from typing import Union

import optuna
import flytekit as fl
from flytekitplugins.optuna import Optimizer, suggest



def test_local_exec():


    @fl.task
    async def objective(x: float, y: int, z: int, power: int) -> float:
        return (((x - 5) ** 2) + (y + 4) ** 4 + (3 * z - 3) ** 2) ** power


