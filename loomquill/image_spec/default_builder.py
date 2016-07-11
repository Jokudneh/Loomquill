import json
import os
import re
import shutil
import sys
import tempfile
import warnings
from pathlib import Path
from string import Template
from subprocess import run
from typing import ClassVar, List, NamedTuple, Tuple

import click

from flytekit.constants import CopyFileDetection
from flytekit.image_spec.image_spec import (
    _F_IMG_ID,
    ImageSpec,
    ImageSpecBuilder,
)
from flytekit.tools.ignore import DockerIgnore, GitIgnore, IgnoreGroup, StandardIgnore
from flytekit.tools.script_mode import ls_files

UV_LOCK_INSTALL_TEMPLATE = Template(
    """\
WORKDIR /root
RUN --mount=type=cache,sharing=locked,mode=0777,target=/root/.cache/uv,id=uv \
    --mount=from=uv,source=/uv,target=/usr/bin/uv \
    --mount=type=bind,target=uv.lock,src=uv.lock \
    --mount=type=bind,target=pyproject.toml,src=pyproject.toml \
    $PIP_SECRET_MOUNT \
    uv sync $PIP_INSTALL_ARGS && \
    chown -R flytekit /root/.venv
WORKDIR /

# Update PATH and UV_PYTHON to point to the venv created by uv sync
ENV PATH="/root/.venv/bin:$$PATH" \
    UV_PYTHON=/root/.venv/bin/python
"""
)

POETRY_LOCK_TEMPLATE = Template(
    """\
RUN --mount=type=cache,sharing=locked,mode=0777,target=/root/.cache/uv,id=uv \
    --mount=from=uv,source=/uv,target=/usr/bin/uv \
    uv pip install poetry

ENV POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_VIRTUALENVS_IN_PROJECT=true

# poetry install does not work running in /, so we move to /root to create the venv
WORKDIR /root

RUN --mount=type=cache,sharing=locked,mode=0777,target=/tmp/poetry_cache,id=poetry \
    --mount=type=bind,target=poetry.lock,src=poetry.lock \
    --mount=type=bind,target=pyproject.toml,src=pyproject.toml \
    $PIP_SECRET_MOUNT \
    poetry install $PIP_INSTALL_ARGS && \
    chown -R flytekit /root/.venv
WORKDIR /

# Update PATH and UV_PYTHON to point to venv
ENV PATH="/root/.venv/bin:$$PATH"  \
    UV_PYTHON=/root/.venv/bin/python
"""
)

UV_PYTHON_INSTALL_COMMAND_TEMPLATE = Template(
    """\
RUN --mount=type=cache,sharing=locked,mode=0777,target=/root/.cache/uv,id=uv \
    --mount=from=uv,source=/uv,target=/usr/bin/uv \
    --mount=type=bind,target=requirements_uv.txt,src=requirements_uv.txt \
    $PIP_SECRET_MOUNT \
    uv pip install $PIP_INSTALL_ARGS
"""
)

# When python_exec points to system Python (e.g. on NVIDIA base images), PEP 668 prevents
# installing packages directly. We create a venv using the base Python and install into it.
# --system-site-packages lets the venv see base image packages (e.g. NVIDIA TensorRT).
UV_PYTHON_VENV_INSTALL_COMMAND_TEMPLATE = Template(
    """\
WORKDIR /root
RUN --mount=type=cache,sharing=locked,mode=0777,target=/root/.cache/uv,id=uv \
    --mount=from=uv,source=/uv,target=/usr/bin/uv \
    --mount=type=bind,target=requirements_uv.txt,src=requirements_uv.txt \
    $PIP_SECRET_MOUNT \
    uv venv --python $BASE_PYTHON_EXEC --system-site-packages /root/.venv && \
    uv pip install --python /root/.venv/bin/python $PIP_INSTALL_ARGS && \
    chown -R flytekit /root/.venv
WORKDIR /
"""
)


APT_INSTALL_COMMAND_TEMPLATE = Template("""\
RUN --mount=type=cache,sharing=locked,mode=0777,target=/var/cache/apt,id=apt \
    apt-get update && apt-get install -y --no-install-recommends \
    $APT_PACKAGES
""")

# make sure that micromamba python installation is owned by flytekit user
MICROMAMBA_INSTALL_COMMAND_TEMPLATE = Template("""\
RUN --mount=type=cache,sharing=locked,mode=0777,target=/opt/micromamba/pkgs,\
id=micromamba \
