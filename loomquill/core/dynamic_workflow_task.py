"""
Dynamic Workflows
-----------------------------
Dynamic workflows are one of the powerful aspects of Flyte. Please take a look at the {{< py_func_ref flytekit.dynamic >}} documentation first to get started.


Caveats when using a dynamic workflow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Because of the dynamic nature of the workflow generated, it can easily be abused. Keep in mind that the workflow
that's compiled out of the decorated function needs to be processed like any other workflow. It's rare to see a
manually written workflow that has 5000 nodes for instance, but you can easily get there with a loop. Please keep,
dynamic workflows to under fifty tasks. For large-scale identical runs, we recommend the upcoming map task.

"""

import functools

from flytekit.core import task
from flytekit.core.python_function_task import PythonFunctionTask

dynamic = functools.partial(task.task, execution_mode=PythonFunctionTask.ExecutionBehavior.DYNAMIC)  # type: ignore[var-annotated]
dynamic.__doc__ = """
Please first see the comments for {{< py_func_ref flytekit.task >}} and {{< py_func_ref flytekit.workflow >}}. This ``dynamic``
concept is an amalgamation of both and enables the user to pursue some :std:ref:`pretty incredible <cookbook:advanced_merge_sort>`
constructs.

In short, a task's function is run at execution time only, and a workflow function is run at compilation time only (local
execution notwithstanding). A dynamic workflow is modeled on the backend as a task, but at execution time, the function
