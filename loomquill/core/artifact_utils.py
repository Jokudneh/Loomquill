from __future__ import annotations

# for why we have the above
# https://github.com/protocolbuffers/protobuf/issues/9765#issuecomment-1119247779
from datetime import datetime
from typing import Dict, Optional

from flyteidl.core.artifact_id_pb2 import Granularity, LabelValue, Partitions, TimePartition
