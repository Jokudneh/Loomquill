def is_serverless_config(databricks_conf: dict) -> bool:
    """
    Detect if the Databricks configuration is for serverless compute.

    Serverless is indicated by having ``environment_key`` or ``environments``
