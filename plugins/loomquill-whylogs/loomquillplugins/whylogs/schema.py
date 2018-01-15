from typing import Type

from flytekit import BlobType, FlyteContext
from flytekit.extend import T, TypeEngine, TypeTransformer
from flytekit.models.literals import Blob, BlobMetadata, Literal, Scalar
from flytekit.models.types import LiteralType
from whylogs.core import DatasetProfileView
from whylogs.viz.extensions.reports.profile_summary import ProfileSummaryReport


class WhylogsDatasetProfileTransformer(TypeTransformer[DatasetProfileView]):
    """
    Transforms whylogs Dataset Profile Views to and from a Schema (typed/untyped)
