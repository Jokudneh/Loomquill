"""
Sleep Fanout Example
====================

Fan out N core-sleep leaves in parallel using map_task.
No task pods are created for the leaves — the backend handles sleep directly.

Usage (remote):
    python sleep_fanout.py
"""

import os
from datetime import timedelta
from typing import List

from flytekitplugins.sleep import Sleep

import flytekit as fl
from flytekit import map_task, task, workflow

sleep_image = fl.ImageSpec(
    registry="ghcr.io/machichima",
    name="sleep-fanout",
    apt_packages=["git"],
    packages=["git+https://github.com/machichima/flytekit.git@add-sleep-plugin#subdirectory=plugins/flytekit-sleep"],
    env={"REBUILD": "1"},
)
