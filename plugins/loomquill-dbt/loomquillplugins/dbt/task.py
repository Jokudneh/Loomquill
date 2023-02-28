import os

from flytekitplugins.dbt.error import DBTHandledError, DBTUnhandledError
from flytekitplugins.dbt.schema import (
    DBTFreshnessInput,
    DBTFreshnessOutput,
    DBTRunInput,
    DBTRunOutput,
    DBTTestInput,
    DBTTestOutput,
)
from flytekitplugins.dbt.util import run_cli

from flytekit import kwtypes
from flytekit.core.interface import Interface
from flytekit.core.python_function_task import PythonInstanceTask
from flytekit.loggers import logger

SUCCESS = 0
HANDLED_ERROR_CODE = 1
UNHANDLED_ERROR_CODE = 2


class DBTRun(PythonInstanceTask):
    """
    Execute DBT Run CLI command.

    The task will execute ``dbt run`` CLI command in a subprocess.
    Input from :class:`flytekitplugins.dbt.schema.DBTRunInput` will be converted into the corresponding CLI flags
    and stored in :class:`flytekitplugins.dbt.schema.DBTRunOutput`'s command.

    Parameters
    ----------
    name : str
        Task name.
    """

    def __init__(
        self,
        name: str,
        **kwargs,
    ):
        super(DBTRun, self).__init__(
            task_type="dbt-run",
            name=name,
            task_config=None,
            interface=Interface(inputs=kwtypes(input=DBTRunInput), outputs=kwtypes(output=DBTRunOutput)),
            **kwargs,
        )

    def execute(self, **kwargs) -> DBTRunOutput:
        """
        This method will be invoked to execute the task.

        Example
        -------
        ::

            dbt_run_task = DBTRun(name="test-task")

            @workflow
            def my_workflow() -> DBTRunOutput:
                return dbt_run_task(
                    input=DBTRunInput(
                        project_dir="tests/jaffle_shop",
                        profiles_dir="tests/jaffle_shop/profiles",
                        profile="jaffle_shop",
                    )
                )


