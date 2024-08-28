from dataclasses import asdict, dataclass
from typing import NamedTuple

import pytest
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from dataclasses_json import DataClassJsonMixin

from flytekit import task, workflow
from flytekit.core.type_engine import TypeTransformerFailedError
from flytekit.extras.pytorch import PyTorchCheckpoint


@dataclass
class Hyperparameters(DataClassJsonMixin):
    epochs: int
    loss: float


class TupleHyperparameters(NamedTuple):
    epochs: int
    loss: float


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
