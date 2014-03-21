import sys
import typing
from collections import OrderedDict

import pytest
from typing_extensions import Annotated

from flytekit import Resources
from flytekit.core.task import task
from flytekit.core.workflow import workflow
from flytekit.types.file import FileExt, FlyteFile
from flytekit.types.schema import FlyteSchema


@pytest.mark.skipif("pandas" not in sys.modules, reason="Pandas is not installed.")
def test_diabetes():
    import pandas as pd

    # Since we are working with a specific dataset, we will create a strictly typed schema for the dataset.
    # If we wanted a generic data splitter we could use a Generic schema without any column type and name information
    # Example file: https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv
    # CSV Columns
    #  1. Number of times pregnant
    #  2. Plasma glucose concentration a 2 hours in an oral glucose tolerance test
    #  3. Diastolic blood pressure (mm Hg)
    #  4. Triceps skin fold thickness (mm)
    #  5. 2-Hour serum insulin (mu U/ml)
    #  6. Body mass index (weight in kg/(height in m)^2)
    #  7. Diabetes pedigree function
    #  8. Age (years)
    #  9. Class variable (0 or 1)
    # Example Row: 6,148,72,35,0,33.6,0.627,50,1
