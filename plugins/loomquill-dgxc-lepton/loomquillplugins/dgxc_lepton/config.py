"""Configuration classes for Lepton AI inference endpoints."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class EndpointType(Enum):
    """Supported endpoint types for Lepton AI."""

    CUSTOM = "custom"
    VLLM = "vllm"
    NIM = "nim"
    SGLANG = "sglang"


class ScalingType(Enum):
    """Supported scaling types for Lepton AI."""

    TRAFFIC = "traffic"
    GPU = "gpu"
    QPM = "qpm"


@dataclass(frozen=True)
class ScalingConfig:
    """Unified scaling configuration that enforces only one scaling type.

    This ensures that only one scaling strategy can be used at a time,
    preventing conflicting scaling configurations.

    Attributes:
        scaling_type (ScalingType): The type of scaling strategy to use
        min_replicas (int): Minimum number of replicas
        max_replicas (int): Maximum number of replicas
        timeout (Optional[int]): Timeout in seconds for traffic-based scaling
        scale_to_zero (Optional[bool]): Whether to allow scaling to zero replicas
        target_utilization (Optional[int]): Target GPU utilization percentage for GPU-based scaling
        target_qpm (Optional[float]): Target queries per minute for QPM-based scaling

    Examples:
        # Traffic-based scaling
        ScalingConfig.traffic(min_replicas=1, max_replicas=3, timeout=1800)

        # GPU-based scaling
        ScalingConfig.gpu(target_utilization=80, min_replicas=1, max_replicas=5)

        # QPM-based scaling
        ScalingConfig.qpm(target_qpm=100.0, min_replicas=2, max_replicas=4)
    """

    scaling_type: ScalingType
    min_replicas: int = 1
    max_replicas: int = 2

    # Traffic scaling parameters
    timeout: Optional[int] = None
    scale_to_zero: Optional[bool] = None

    # GPU scaling parameters
    target_utilization: Optional[int] = None

    # QPM scaling parameters
    target_qpm: Optional[float] = None

    def __post_init__(self):
        """Validate scaling configuration parameters."""
        if self.scaling_type == ScalingType.TRAFFIC:
            if self.timeout is None:
                object.__setattr__(self, "timeout", 3600)  # Default timeout
            if self.scale_to_zero is None:
                object.__setattr__(self, "scale_to_zero", False)
        elif self.scaling_type == ScalingType.GPU:
            if self.target_utilization is None:
                raise ValueError("target_utilization is required for GPU scaling")
            if not 1 <= self.target_utilization <= 100:
                raise ValueError("target_utilization must be between 1 and 100")
        elif self.scaling_type == ScalingType.QPM:
            if self.target_qpm is None:
                raise ValueError("target_qpm is required for QPM scaling")
