import geopandas as gpd
from flytekitplugins.geopandas.gdf_transformers import GeoPandasDataFrameRenderer
from pathlib import Path

import pytest

from flytekit import task
from flytekit.types.structured.structured_dataset import StructuredDataset
import numpy as np


def test_geopandas_encodes_decodes():
    @task
    def _gdf_task(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        return gdf

    gdf = gpd.GeoDataFrame(
        {"geometry": gpd.points_from_xy([0, 1], [0, 1]), "other_column": [1, 2]},
