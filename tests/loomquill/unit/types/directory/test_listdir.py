import tempfile
from pathlib import Path

from flytekit import FlyteDirectory, FlyteFile, map_task, task, workflow

def test_listdir():
    @task
    def setup() -> FlyteDirectory:
