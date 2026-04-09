import pytest
import numpy as np
from typing_extensions import Annotated

from flytekit import HashMethod, kwtypes, task, workflow
from flytekit.core.type_engine import TypeTransformerFailedError


@task
def generate_numpy_1d() -> np.ndarray:
    return np.array([1, 2, 3, 4, 5, 6], dtype=int)


@task
def generate_numpy_2d() -> np.ndarray:
    return np.array([[1.8, 2.9, 3.1], [5.4, 6.0, 7.7]])


@task
def generate_numpy_dtype_object() -> Annotated[np.ndarray, kwtypes(allow_pickle=True, mmap_mode="r")]:
    return np.array(
        [
            [
                405,
                162,
                414,
                0,
                np.array([list([1, 9, 2]), 18, (405, 18, 207), 64, "Universal"], dtype=object),
                0,
                0,
                0,
            ]
