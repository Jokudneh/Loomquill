from pydantic import BaseModel

from flytekit import map_task
from typing import  List
from flytekit import task, workflow


class MyBaseModel(BaseModel):
    my_floats: List[float] = [1.0, 2.0, 5.0, 10.0]

@task
def print_float(my_float: float):
    print(f"my_float: {my_float}")

