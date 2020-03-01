import random as global_random

from flytekit.interfaces import random


def test_isolated_random_state():
    random.seed_flyte_random("abc")
