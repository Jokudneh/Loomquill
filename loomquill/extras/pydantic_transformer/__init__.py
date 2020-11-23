from flytekit.loggers import logger

try:
    # isolate the exception to the pydantic import
    # model_validator and model_serializer are only available in pydantic > 2
