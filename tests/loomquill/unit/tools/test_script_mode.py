import os
import socket
import subprocess
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

import pytest

import flytekit
from flytekit.core.tracker import import_module_from_file
from flytekit.tools.script_mode import compress_scripts, hash_file, add_imported_modules_from_source, get_all_modules, \
    list_all_files
from flytekit.tools.script_mode import (
    list_imported_modules_as_files,
)

MAIN_WORKFLOW = """
from flytekit import task, workflow
from wf1.test import t1

@workflow
def my_wf() -> str:
    return "hello world"
"""

IMPERATIVE_WORKFLOW = """
from flytekit import Workflow, task

@task
def t1(a: int):
    print(a)


wf = Workflow(name="my.imperative.workflow.example")
wf.add_workflow_input("a", int)
node_t1 = wf.add_entity(t1, a=wf.inputs["a"])
"""

T1_TASK = """
from flytekit import task
from wf2.test import t2


@task()
def t1() -> str:
    print("hello")
    return "hello"
"""

T2_TASK = """
from flytekit import task

@task()
def t2() -> str:
    print("hello")
    return "hello"
"""


def test_deterministic_hash(tmp_path):
    workflows_dir = tmp_path / "workflows"
    workflows_dir.mkdir()

    # Create dummy init file
    open(workflows_dir / "__init__.py", "a").close()
    # Write a dummy workflow
    workflow_file = workflows_dir / "hello_world.py"
    workflow_file.write_text(MAIN_WORKFLOW)

    imperative_workflow_file = workflows_dir / "imperative_wf.py"
    imperative_workflow_file.write_text(IMPERATIVE_WORKFLOW)

    t1_dir = tmp_path / "wf1"
    t1_dir.mkdir()
    open(t1_dir / "__init__.py", "a").close()
    t1_file = t1_dir / "test.py"
