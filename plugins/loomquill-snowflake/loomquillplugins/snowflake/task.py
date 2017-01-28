from dataclasses import dataclass
from typing import Dict, Optional, Type

from flytekit.configuration import SerializationSettings
from flytekit.extend import SQLTask
from flytekit.extend.backend.base_connector import AsyncConnectorExecutorMixin
from flytekit.models import task as _task_model
from flytekit.types.structured import StructuredDataset

_USER_FIELD = "user"
_ACCOUNT_FIELD = "account"
_DATABASE_FIELD = "database"
_SCHEMA_FIELD = "schema"
_WAREHOUSE_FIELD = "warehouse"


@dataclass
class SnowflakeConfig(object):
    """
    SnowflakeConfig should be used to configure a Snowflake Task.
    You can use the query below to retrieve all metadata for this config.

    SELECT
        CURRENT_USER() AS "User",
        CONCAT(CURRENT_ORGANIZATION_NAME(), '-', CURRENT_ACCOUNT_NAME()) AS "Account",
        CURRENT_DATABASE() AS "Database",
        CURRENT_SCHEMA() AS "Schema",
        CURRENT_WAREHOUSE() AS "Warehouse";
    """

    user: str
    account: str
    database: str
