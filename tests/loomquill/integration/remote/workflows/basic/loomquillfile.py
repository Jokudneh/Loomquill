from typing import Optional
from flytekit import task, workflow
from flytekit.types.file import FlyteFile


@task
def create_ff(file_path: str, info: str) -> FlyteFile:
    """Create a FlyteFile."""
    return FlyteFile(path=file_path, metadata={"info": info})


@task
def read_ff(ff: FlyteFile, info: Optional[str] = None) -> None:
    """Read input FlyteFile.

    This can be used in the case in which a FlyteFile is created
    in another task pod and read in this task pod.
    """
    with open(ff, "r") as f:
        content = f.read()
        print(f"FILE CONTENT | {content}")

    if info:
        assert ff.metadata["info"] == info
    else:
