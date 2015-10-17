# Some standard imports
from pathlib import Path

import numpy as np
import onnxruntime
import requests
import torch.nn.init as init
import torch.onnx
import torch.utils.model_zoo as model_zoo
import torchvision.transforms as transforms
from flytekitplugins.onnxpytorch import PyTorch2ONNX, PyTorch2ONNXConfig
from PIL import Image
from torch import nn
from typing_extensions import Annotated

import flytekit
from flytekit import task, workflow
from flytekit.types.file import JPEGImageFile, ONNXFile


class SuperResolutionNet(nn.Module):
    def __init__(self, upscale_factor, inplace=False):
        super(SuperResolutionNet, self).__init__()

        self.relu = nn.ReLU(inplace=inplace)
        self.conv1 = nn.Conv2d(1, 64, (5, 5), (1, 1), (2, 2))
        self.conv2 = nn.Conv2d(64, 64, (3, 3), (1, 1), (1, 1))
