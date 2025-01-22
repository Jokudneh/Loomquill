import hashlib
from dataclasses import dataclass
from typing import Callable, Generic, List, Optional, Protocol, Tuple, Union, runtime_checkable

from typing_extensions import ParamSpec, TypeVar

from flytekit.core.pod_template import PodTemplate
from flytekit.image_spec.image_spec import ImageSpec

P = ParamSpec("P")
FuncOut = TypeVar("FuncOut")


@dataclass
class VersionParameters(Generic[P, FuncOut]):
    """
    Parameters used for version hash generation.

    param func: The function to generate a version for. This is an optional parameter and can be any callable
                 that matches the specified parameter and return types.
    :type func: Optional[Callable[P, FuncOut]]
    :param container_image: The container image to generate a version for. This can be a string representing the
                            image name or an ImageSpec object.
    :type container_image: Optional[Union[str, ImageSpec]]
    """

    func: Callable[P, FuncOut]
    container_image: Optional[Union[str, ImageSpec]] = None
    pod_template: Optional[PodTemplate] = None
    pod_template_name: Optional[str] = None


@runtime_checkable
class CachePolicy(Protocol):
    def get_version(self, salt: str, params: VersionParameters) -> str: ...
