"""
These classes provide functionality related context management.
"""

from __future__ import annotations

import logging as _logging
import os
import pathlib
import signal
import tempfile
import threading
import traceback
import typing
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import FrameType
from typing import Generator, List, Optional, Union

from flytekit.configuration import Config, SecretsConfig, SerializationSettings
from flytekit.core import mock_stats, utils
from flytekit.core.checkpointer import Checkpoint, SyncCheckpoint
from flytekit.core.data_persistence import FileAccessProvider, default_local_file_access_provider
from flytekit.core.node import Node
from flytekit.interfaces.cli_identifiers import WorkflowExecutionIdentifier
from flytekit.interfaces.stats import taggable
from flytekit.loggers import developer_logger, user_space_logger
from flytekit.models.core import identifier as _identifier

if typing.TYPE_CHECKING:
    from flytekit.clients import friendly as friendly_client  # noqa
    from flytekit.clients.friendly import SynchronousFlyteClient
    from flytekit.core.worker_queue import Controller
    from flytekit.deck.deck import Deck

# TODO: resolve circular import from flytekit.core.python_auto_container import TaskResolverMixin

# Enables static type checking https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING

flyte_context_Var: ContextVar[typing.List[FlyteContext]] = ContextVar("", default=[])

if typing.TYPE_CHECKING:
    from flytekit.core.base_task import Task, TaskResolverMixin


# Identifier fields use placeholders for registration-time substitution.
# Additional fields, such as auth and the raw output data prefix have more complex structures
# and can be optional so they are not serialized with placeholders.

# During out of container serialize the absolute path of the flytekit virtualenv at serialization time won't match the
# in-container value at execution time. The following default value is used to provide the in-container virtualenv path
# but can be optionally overridden at serialization time based on the installation of your flytekit virtualenv.


class ExecutionParameters(object):
    """
    This is a run-time user-centric context object that is accessible to every @task method. It can be accessed using


    ```python
    flytekit.current_context()
    ```

    This object provides the following objections
    * a statsd handler
    * a logging handler
    * the execution ID as an `flytekit.models.core.identifier.WorkflowExecutionIdentifier` object
    * a working directory for the user to write arbitrary files to

    Please do not confuse this object with the `flytekit.FlyteContext` object.
    """

    @dataclass(init=False)
    class Builder(object):
        stats: taggable.TaggableStats
        attrs: typing.Dict[str, typing.Any]
        decks: List[Deck]
        raw_output_prefix: Optional[str] = None
        execution_id: typing.Optional[_identifier.WorkflowExecutionIdentifier] = None
        working_dir: typing.Optional[str] = None
        checkpoint: typing.Optional[Checkpoint] = None
        execution_date: typing.Optional[datetime] = None
        logging: Optional[_logging.Logger] = None
        task_id: typing.Optional[_identifier.Identifier] = None
        output_metadata_prefix: Optional[str] = None
        enable_deck: bool = False

        def __init__(self, current: typing.Optional[ExecutionParameters] = None):
            self.stats = current.stats if current else None
            self.execution_date = current.execution_date if current else None
            self.working_dir = current.working_directory if current else None
            self.execution_id = current.execution_id if current else None
            self.logging = current.logging if current else None
            self.checkpoint = current._checkpoint if current else None
            self.decks = current._decks if current else []
            self.attrs = current._attrs if current else {}
            self.raw_output_prefix = current.raw_output_prefix if current else None
            self.task_id = current.task_id if current else None
            self.output_metadata_prefix = current.output_metadata_prefix if current else None
            self.enable_deck = current.enable_deck if current else False

        def add_attr(self, key: str, v: typing.Any) -> ExecutionParameters.Builder:
            self.attrs[key] = v
            return self

        def build(self) -> ExecutionParameters:
            if self.working_dir and not isinstance(self.working_dir, utils.AutoDeletingTempDir):
                pathlib.Path(typing.cast(str, self.working_dir)).mkdir(parents=True, exist_ok=True)
            return ExecutionParameters(
                execution_date=self.execution_date,
                stats=self.stats,
                tmp_dir=self.working_dir,
                execution_id=self.execution_id,
                logging=self.logging,
                checkpoint=self.checkpoint,
                decks=self.decks,
                raw_output_prefix=self.raw_output_prefix,
                task_id=self.task_id,
                output_metadata_prefix=self.output_metadata_prefix,
                enable_deck=self.enable_deck,
                **self.attrs,
            )

    @staticmethod
    def new_builder(current: Optional[ExecutionParameters] = None) -> Builder:
        return ExecutionParameters.Builder(current=current)

    def with_task_sandbox(self) -> Builder:
        prefix = self.working_directory
        if isinstance(self.working_directory, utils.AutoDeletingTempDir):
            prefix = self.working_directory.name
        task_sandbox_dir = tempfile.mkdtemp(prefix=prefix)  # type: ignore
        p = pathlib.Path(task_sandbox_dir)
        cp_dir = p / "__cp"
        cp_dir.mkdir(exist_ok=True)
        cp = SyncCheckpoint(checkpoint_dest=str(cp_dir))
        b = self.new_builder(self)
        b.checkpoint = cp
        b.working_dir = task_sandbox_dir
        return b

    def with_enable_deck(self, enable_deck: bool) -> Builder:
        b = self.new_builder(self)
        b.enable_deck = enable_deck
        return b

    def builder(self) -> Builder:
        return ExecutionParameters.Builder(current=self)

    def __repr__(self):
        cp = f" checkpoint={self.checkpoint}," if self._checkpoint else ""
        return (
            f"ExecutionParameters(execution_date={self.execution_date},"
            f" stats={self.stats},"
            f" tmp_dir={self.working_directory},"
            f" execution_id={self.execution_id},"
            f" {cp},"
            f" decks={self.decks},"
            f" raw_output_prefix={self.raw_output_prefix},"
            f" task_id={self.task_id},"
            f" output_metadata_prefix={self.output_metadata_prefix},"
            f" enable_deck={self.enable_deck})"
        )

    def __init__(
        self,
        execution_date,
        tmp_dir,
        stats,
        execution_id: typing.Optional[_identifier.WorkflowExecutionIdentifier],
        logging,
        raw_output_prefix,
        output_metadata_prefix=None,
        checkpoint=None,
        decks=None,
        task_id: typing.Optional[_identifier.Identifier] = None,
        enable_deck: bool = False,
        **kwargs,
    ):
        """
        Args:
            execution_date: Date when the execution is running
            tmp_dir: temporary directory for the execution
            stats: handle to emit stats
            execution_id: Identifier for the execution
            logging: handle to logging
            checkpoint: Checkpoint Handle to the configured checkpoint system
        """
        if decks is None:
            decks = []
        self._stats = stats
        self._execution_date = execution_date
        self._working_directory = tmp_dir
        self._execution_id = execution_id
        self._logging = logging
        self._raw_output_prefix = raw_output_prefix
        self._output_metadata_prefix = output_metadata_prefix
        # AutoDeletingTempDir's should be used with a with block, which creates upon entry
        self._attrs = kwargs
        # It is safe to recreate the Secrets Manager
        self._secrets_manager = SecretsManager()
        self._checkpoint = checkpoint
        self._decks = decks
        self._task_id = task_id
        self._timeline_deck = None
        self._enable_deck = enable_deck

    @property
    def stats(self) -> taggable.TaggableStats:
        """
        A handle to a special statsd object that provides usefully tagged stats.
        TODO: Usage examples and better comments
        """
        return self._stats

    @property
    def logging(self) -> _logging.Logger:
        """
        A handle to a useful logging object.
        TODO: Usage examples
        """
        return self._logging

    @property
    def raw_output_prefix(self) -> str:
        return self._raw_output_prefix

    @property
    def output_metadata_prefix(self) -> str:
        return self._output_metadata_prefix

    @property
    def working_directory(self) -> str:
        """
        A handle to a special working directory for easily producing temporary files.
        TODO: Usage examples
        """
        return self._working_directory

    @property
    def execution_date(self) -> datetime:
        """
        This is a datetime representing the time at which a workflow was started.  This is consistent across all tasks
        executed in a workflow or sub-workflow.

        > [!NOTE]
        > Do NOT use this execution_date to drive any production logic.  It might be useful as a tag for data to help
            in debugging.
        """
        return self._execution_date

    @property
    def execution_id(self) -> _identifier.WorkflowExecutionIdentifier:
        """
        This is the identifier of the workflow execution within the underlying engine.  It will be consistent across all
        task executions in a workflow or sub-workflow execution.

        > [!NOTE]
        > Do NOT use this execution_id to drive any production logic.  This execution ID should only be used as a tag
            on output data to link back to the workflow run that created it.
        """
        return self._execution_id

