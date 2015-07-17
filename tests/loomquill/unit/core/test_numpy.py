from collections import OrderedDict

import numpy as np
from numpy.testing import assert_array_equal

import flytekit
from flytekit import task
from flytekit.configuration import Image, ImageConfig
from flytekit.core import context_manager
from flytekit.models.core.types import BlobType
from flytekit.models.literals import BlobMetadata
from flytekit.models.types import LiteralType
