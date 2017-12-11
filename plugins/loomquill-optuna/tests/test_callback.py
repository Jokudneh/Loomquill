from typing import Union

import asyncio
from typing import Union
import optuna

import flytekit as fl
from flytekitplugins.optuna import Optimizer


def test_callback():


    @fl.task
    async def objective(letter: str, number: Union[float, int], other: str, fixed: str) -> float:

        loss = len(letter) + number + len(other) + len(fixed)

        return float(loss)

    def callback(trial: optuna.Trial, fixed: str):

        letter = trial.suggest_categorical("booster", ["A", "B", "BLAH"])

        if letter == "A":
            number = trial.suggest_int("number_A", 1, 10)
