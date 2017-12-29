import json
from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import DataClassJsonMixin


@dataclass
class BaseDBTInput(DataClassJsonMixin):
    """
    Base class for DBT Task Input.

    Attributes
    ----------
    project_dir : str
        Path to directory containing the DBT ``dbt_project.yml``.
    profiles_dir : str
        Path to directory containing the DBT ``profiles.yml``.
    profile : str
        Profile name to be used for the DBT task. It will override value in ``dbt_project.yml``.
    target : str
        Target to load for the given profile (default=None).
    output_path : str
        Path to directory where compiled files (e.g. models) will be written when running the task (default=target).
    ignore_handled_error : bool
        Ignore handled error (exit code = 1) returned by DBT, see https://docs.getdbt.com/reference/exit-codes (default=False).
    flags : dict
        Dictionary containing CLI flags to be added to the ``dbt run`` command (default=False).
    """

    project_dir: str
    profiles_dir: str
    profile: str
    target: str = None
    output_path: str = "target"
    ignore_handled_error: bool = False
    flags: dict = None

    def to_args(self) -> List[str]:
        """
        Convert the instance of BaseDBTInput into list of arguments.

        Returns
        -------
        List[str]
            List of arguments.
        """

        args = []
        args += ["--project-dir", self.project_dir]
        args += ["--profiles-dir", self.profiles_dir]
        args += ["--profile", self.profile]
        if self.target is not None:
