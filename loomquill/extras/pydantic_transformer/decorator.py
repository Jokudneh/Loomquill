import logging
from typing import Any, Callable, TypeVar, Union

logger = logging.getLogger(__name__)

try:
    # isolate the exception to the pydantic import
    # model_validator and model_serializer are only available in pydantic > 2
    from pydantic import model_serializer, model_validator

except ImportError:
    """
    It's to support the case where pydantic is not installed at all.
    It looks nicer in the real Flyte File/Directory class, but we also want it to not fail.
    """

    logger.debug(
        "Pydantic is not installed.\n" "Please install Pydantic version > 2 to use FlyteTypes in pydantic BaseModel."
    )

    FuncType = TypeVar("FuncType", bound=Callable[..., Any])

    from typing_extensions import Literal as typing_literal
