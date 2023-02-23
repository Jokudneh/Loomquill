from __future__ import annotations

from typing import Any, Generic, Optional, Type, TypeVar, Union, cast

from flytekit.core.context_manager import ExecutionParameters, ExecutionState, FlyteContext, FlyteContextManager
from flytekit.core.tracker import TrackedInstance
from flytekit.core.type_engine import TypeEngine
from flytekit.loggers import logger
from flytekit.models import dynamic_job as _dynamic_job
from flytekit.models import literals as _literal_models
from flytekit.models import task as _task_model


class ExecutableTemplateShimTask(object):
    """
    The canonical ``@task`` decorated Python function task is pretty simple to reason about. At execution time (either
    locally or on a Flyte cluster), the function runs.

    This class, along with the ``ShimTaskExecutor`` class below, represents another execution pattern. This pattern,
    has two components:

    * The ``TaskTemplate``, or something like it like a ``FlyteTask``.
    * An executor, which can use information from the task template (including the ``custom`` field)

    Basically at execution time (both locally and on a Flyte cluster), the task template is given to the executor,
    which is responsible for computing and returning the results.

    > [!NOTE]
    > The interface at execution time will have to derived from the Flyte IDL interface, which means it may be lossy.
      This is because when a task is serialized from Python into the ``TaskTemplate`` some information is lost because
       Flyte IDL can't keep track of every single Python type (or Java type if writing in the Java flytekit).
