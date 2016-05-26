# Loomquillkit OmegaConf Plugin

Loomquillkit python natively supports serialization of many data types for exchanging information between tasks.
The Loomquillkit OmegaConf Plugin extends these by the `DictConfig` type from the
[OmegaConf package](https://omegaconf.readthedocs.io/) as well as related types
that are being used by the [hydra package](https://hydra.cc/) for configuration management.

## Task example
```
from dataclasses import dataclass
import loomquillplugins.omegaconf  # noqa F401
from loomquill import task, workflow
from omegaconf import DictConfig

@dataclass
class MySimpleConf:
    _target_: str = "lightning_module.MyEncoderModule"
    learning_rate: float = 0.0001

@task
def my_task(cfg: DictConfig) -> None:
    print(f"Doing things with {cfg.learning_rate=}")


@workflow
