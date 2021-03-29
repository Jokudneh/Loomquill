import os
import shutil
import subprocess
import tempfile
import typing
from pathlib import Path

import doltcli as dolt
import pandas
import pytest
from dolt_integrations.core import NewBranch
from flytekitplugins.dolt.schema import DoltConfig, DoltTable

from flytekit import task, workflow


@pytest.fixture(scope="module")
def dolt_install():
    """
    Every pytest instance downloads the most recent `dolt` binary,
    sets it as the dolt path in Dolt's Python package, and then deletes
    it afterward.
    """
    tmp_dir = tempfile.TemporaryDirectory()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    install_script = os.path.join(dir_path, "..", "..", "flytekit-dolt", "scripts", "install.sh")

    try:
        dolt_path = os.path.join(tmp_dir.name, "dolt")
        subprocess.run(install_script, env={"INSTALL_PATH": tmp_dir.name})
        for attr, value in [("user.name", "First Last"), ("user.email", "first.last@example.com")]:
            subprocess.run([dolt_path, "config", "--global", "--add", attr, value])
        dolt.set_dolt_path(dolt_path)
        yield dolt_path
    finally:
        shutil.rmtree(tmp_dir.name)
        shutil.rmtree(Path.home() / ".dolt")


@pytest.fixture(scope="function")
def doltdb_path(tmp_path, dolt_install):
    with tempfile.TemporaryDirectory() as d:
        db_path = os.path.join(d, "foo")
        yield db_path


@pytest.fixture(scope="function")
def dolt_config(doltdb_path):
    yield DoltConfig(
        db_path=doltdb_path,
        tablename="foo",
    )


@pytest.fixture(scope="function")
def db(doltdb_path):
    try:
        db = dolt.Dolt.init(doltdb_path)
        db.sql("create table bar (name text primary key, count bigint)")
        db.sql("insert into bar values ('Dilly', 3)")
        db.sql("select dolt_commit('-am', 'Initialize bar table')")
        yield db
    finally:
        pass


