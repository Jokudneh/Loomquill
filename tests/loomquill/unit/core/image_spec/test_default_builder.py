import re
import os
from unittest.mock import patch, Mock

import pytest

import flytekit
from flytekit.image_spec import ImageSpec
from flytekit.image_spec.default_builder import DefaultImageBuilder, create_docker_context
from flytekit.constants import CopyFileDetection
from pathlib import Path
import tempfile

def test_create_docker_context(tmp_path):
    docker_context_path = tmp_path / "builder_root"
    docker_context_path.mkdir()

    source_root = tmp_path / "other_files"
    source_root.mkdir()
    hello_world_path = source_root / "hello_world.txt"
    hello_world_path.write_text("hello")

    other_requirements_path = tmp_path / "requirements.txt"
    other_requirements_path.write_text("threadpoolctl\n")

    with tempfile.TemporaryDirectory(dir=Path.cwd().as_posix()) as tmp_dir:
        tmp_file = Path(tmp_dir) / "copy_file.txt"
        tmp_file.write_text("copy_file_content")

        image_spec = ImageSpec(
            name="FLYTEKIT",
            python_version="3.12",
            env={"MY_ENV": "MY_VALUE"},
            apt_packages=["curl"],
            conda_packages=["scipy==1.13.0", "numpy"],
            packages=["pandas==2.2.1"],
            requirements=os.fspath(other_requirements_path),
            source_root=os.fspath(source_root),
            commands=["mkdir my_dir"],
            entrypoint=["/bin/bash"],
            pip_index="https://url.com",
            pip_extra_index_url=["https://extra-url.com"],
            pip_secret_mounts=[(".gitconfig", '/etc/gitconfig'), ("secret_src_2", "secret_dst_2")],
            source_copy_mode=CopyFileDetection.ALL,
            copy=[tmp_file.relative_to(Path.cwd()).as_posix()],
            builder_config={"uv_image": "uv_image_local"},
        )

        create_docker_context(image_spec, docker_context_path)

    dockerfile_path = docker_context_path / "Dockerfile"
    assert dockerfile_path.exists()
    dockerfile_content = dockerfile_path.read_text()

    assert "curl" in dockerfile_content
    assert "scipy==1.13.0 numpy" in dockerfile_content
    assert "python=3.12" in dockerfile_content
    assert "--requirement requirements_uv.txt" in dockerfile_content
    assert "--index-url" in dockerfile_content
    assert "--extra-index-url" in dockerfile_content
    assert "--mount=type=secret,id=secret_0,target=/etc/gitconfig" in dockerfile_content
    assert "--mount=type=secret,id=secret_1,target=secret_dst_2" in dockerfile_content
    assert "COPY --chown=flytekit ./src /root" in dockerfile_content
    assert "uv_image_local" in dockerfile_content
    assert "mambaorg/micromamba:2.0.3-debian12-slim" in dockerfile_content

    run_match = re.search(r"RUN.+mkdir my_dir", dockerfile_content)
    assert run_match
    assert "ENTRYPOINT [\"/bin/bash\"]" in dockerfile_content
    assert "mkdir -p $HOME" in dockerfile_content
    assert f"COPY --chown=flytekit {tmp_file.relative_to(Path.cwd()).as_posix()} /root/" in dockerfile_content

    requirements_path = docker_context_path / "requirements_uv.txt"
    assert requirements_path.exists()

    requirements_content = requirements_path.read_text()
    assert "pandas==2.2.1" in requirements_content
    assert "threadpoolctl" in requirements_content

    tmp_hello_world = docker_context_path / "src" / "hello_world.txt"
    assert tmp_hello_world.exists()
    assert tmp_hello_world.read_text() == "hello"


def test_create_docker_context_with_git_subfolder(tmp_path):
    # uv's pip install errors with git and subdirectory
    # In this case, we go back to pip instead
    docker_context_path = tmp_path / "builder_root"
    docker_context_path.mkdir()

    image_spec = ImageSpec(
        name="FLYTEKIT",
        python_version="3.12",
        apt_packages=["git"],
        packages=["git+https://github.com/flyteorg/flytekit.git@master#subdirectory=plugins/flytekit-wandb"],
    )

    create_docker_context(image_spec, docker_context_path)

    dockerfile_path = docker_context_path / "Dockerfile"
    assert dockerfile_path.exists()
    dockerfile_content = dockerfile_path.read_text()

    assert "--requirement requirements_uv.txt" in dockerfile_content
