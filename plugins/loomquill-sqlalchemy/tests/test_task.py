import contextlib
import os
import shutil
import sqlite3
import tempfile
from typing import Iterator
from unittest import mock

import pandas
import pytest
from click.testing import CliRunner
from flytekitplugins.sqlalchemy import SQLAlchemyConfig, SQLAlchemyTask
from flytekitplugins.sqlalchemy.task import SQLAlchemyTaskExecutor

from flytekit import kwtypes, task, workflow
from flytekit.clients.friendly import SynchronousFlyteClient
from flytekit.clis.sdk_in_container import pyflyte
from flytekit.core import context_manager
from flytekit.core.context_manager import SecretsManager
from flytekit.models.security import Secret
from flytekit.remote import FlyteRemote
from flytekit.types.schema import FlyteSchema

tk = SQLAlchemyTask(
    "test",
    query_template="select * from tracks",
    task_config=SQLAlchemyConfig(
        uri="sqlite://",
    ),
)


@pytest.fixture(scope="function")
def sql_server() -> Iterator[str]:
    d = tempfile.TemporaryDirectory()
    try:
        db_path = os.path.join(d.name, "tracks.db")
        with contextlib.closing(sqlite3.connect(db_path)) as con:
            con.execute("create table tracks (TrackId bigint, Name text)")
            con.execute("insert into tracks values (0, 'Sue'), (1, 'L'), (2, 'M'), (3, 'Ji'), (4, 'Po')")
            con.commit()
        yield f"sqlite:///{db_path}"
    finally:
