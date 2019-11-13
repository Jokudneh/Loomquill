from abc import ABC

from flytekit.core.tracker import TrackedInstance


class FlyteTrackedABC(type(TrackedInstance), type(ABC)):  # type: ignore
    """
