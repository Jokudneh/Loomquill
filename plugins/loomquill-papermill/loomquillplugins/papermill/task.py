import json
import logging
import os
import sys
import tempfile
import typing
from typing import Any

from flyteidl.core.literals_pb2 import Literal as _pb2_Literal
from flyteidl.core.literals_pb2 import LiteralMap as _pb2_LiteralMap
from google.protobuf import text_format as _text_format

from flytekit import FlyteContext, PythonInstanceTask, StructuredDataset, lazy_module
from flytekit.configuration import SerializationSettings
from flytekit.core import utils
from flytekit.core.context_manager import ExecutionParameters
from flytekit.core.tracker import extract_task_module
from flytekit.deck.deck import Deck
from flytekit.extend import Interface, TaskPlugins, TypeEngine
from flytekit.loggers import logger
from flytekit.models import task as task_models
from flytekit.models.literals import Literal, LiteralMap
from flytekit.types.directory import FlyteDirectory
from flytekit.types.file import FlyteFile, HTMLPage, PythonNotebook

T = typing.TypeVar("T")

nbformat = lazy_module("nbformat")
pm = lazy_module("papermill")
nbconvert = lazy_module("nbconvert")


def _dummy_task_func():
    return None


SAVE_AS_LITERAL = (FlyteFile, FlyteDirectory, StructuredDataset)

PAPERMILL_TASK_PREFIX = "pm.nb"


class NotebookTask(PythonInstanceTask[T]):
    """
    Simple Papermill based input output handling for a Python Jupyter notebook. This task should be used to wrap
    a Notebook that has 2 properties

    Property 1:
    One of the cells (usually the first) should be marked as the parameters cell. This task will inject inputs after this
    cell. The task will inject the outputs observed from Flyte

    Property 2:
    For a notebook that produces outputs, that should be consumed by a subsequent notebook, use the method
    {{< py_func_ref record_outputs >}} in your notebook after the outputs are ready and pass all outputs.

    Usage:

    .. code-block:: python

        val_x = 10
        val_y = "hello"

        ...
        # cell begin
        from flytekitplugins.papermill import record_outputs

        record_outputs(x=val_x, y=val_y)
        #cell end

    Step 2: Wrap in a task
    Now point to the notebook and create an instance of {{< py_class_ref NotebookTask >}} as follows

    Usage:

    .. code-block:: python

        nb = NotebookTask(
            name="modulename.my_notebook_task", # the name should be unique within all your tasks, usually it is a good
                                               # idea to use the modulename
            notebook_path="../path/to/my_notebook",
            render_deck=True,
            enable_deck=True,
            inputs=kwtypes(v=int),
            outputs=kwtypes(x=int, y=str),
            metadata=TaskMetadata(retries=3, cache=True, cache_version="1.0"),
        )
