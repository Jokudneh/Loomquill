import os

import pytest
from hypothesis import settings

from flytekit.image_spec.image_spec import ImageSpecBuilder


class MockImageSpecBuilder(ImageSpecBuilder):
    def build_image(self, img):
        print("Building an image...")

