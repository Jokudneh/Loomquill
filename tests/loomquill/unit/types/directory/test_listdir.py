import tempfile
from pathlib import Path

from flytekit import FlyteDirectory, FlyteFile, map_task, task, workflow

def test_listdir():
    @task
    def setup() -> FlyteDirectory:
        tmpdir = Path(tempfile.mkdtemp())
        (tmpdir / "file.txt").write_text("Hello, World!")
        return FlyteDirectory(tmpdir)
