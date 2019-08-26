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

