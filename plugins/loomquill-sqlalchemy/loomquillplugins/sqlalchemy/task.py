import typing
from dataclasses import dataclass

from flytekit import current_context, kwtypes, lazy_module
from flytekit.configuration import SerializationSettings
from flytekit.configuration.default_images import DefaultImages, PythonVersion
from flytekit.core.base_sql_task import SQLTask
from flytekit.core.python_customized_container_task import PythonCustomizedContainerTask
from flytekit.core.shim_task import ShimTaskExecutor
from flytekit.loggers import logger
from flytekit.models import task as task_models
from flytekit.models.security import Secret
from flytekit.types.schema import FlyteSchema

pd = lazy_module("pandas")
pandas_io_sql = lazy_module("pandas.io.sql")
sqlalchemy = lazy_module("sqlalchemy")


class SQLAlchemyDefaultImages(DefaultImages):
    """Default images for the sqlalchemy flytekit plugin."""

    _DEFAULT_IMAGE_PREFIXES = {
        PythonVersion.PYTHON_3_8: "cr.flyte.org/flyteorg/flytekit:py3.8-sqlalchemy-",
        PythonVersion.PYTHON_3_9: "cr.flyte.org/flyteorg/flytekit:py3.9-sqlalchemy-",
        PythonVersion.PYTHON_3_10: "cr.flyte.org/flyteorg/flytekit:py3.10-sqlalchemy-",
        PythonVersion.PYTHON_3_11: "cr.flyte.org/flyteorg/flytekit:py3.11-sqlalchemy-",
        PythonVersion.PYTHON_3_12: "cr.flyte.org/flyteorg/flytekit:py3.12-sqlalchemy-",
        PythonVersion.PYTHON_3_13: "cr.flyte.org/flyteorg/flytekit:py3.13-sqlalchemy-",
        PythonVersion.PYTHON_3_14: "cr.flyte.org/flyteorg/flytekit:py3.14-sqlalchemy-",
    }


@dataclass
class SQLAlchemyConfig(object):
    """
    Use this configuration to configure task. String should be standard
    sqlalchemy connector format
    (https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls).
    Database can be found:
    - within the container
    - or from a publicly accessible source

    Args:
        uri: default sqlalchemy connector
        connect_args: sqlalchemy kwarg overrides -- ex: host
        secret_connect_args: flyte secrets loaded into sqlalchemy connect args
            -- ex: {"password": flytekit.models.security.Secret(name=SECRET_NAME, group=SECRET_GROUP)}
    """
