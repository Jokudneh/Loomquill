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
def pipeline(cfg: DictConfig) -> None:
    my_task(cfg=cfg)


if __name__ == "__main__":
    from omegaconf import OmegaConf

    cfg = OmegaConf.structured(MySimpleConf)
    pipeline(cfg=cfg)
```

## Transformer configuration

The transformer can be set to one of three modes:

`Dataclass` - This mode should be used with a StructuredConfig and will reconstruct the config from the matching dataclass
during deserialisation in order to make typing information from the dataclass and continued validation thereof available.
This requires the dataclass definition to be available via python import in the Loomquill execution environment in which
objects are (de-)serialised.

