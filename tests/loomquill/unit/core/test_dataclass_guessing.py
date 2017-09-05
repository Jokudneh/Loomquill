from typing import List, Optional

from pydantic import BaseModel

from flytekit.core.type_engine import TypeEngine, strict_type_hint_matching
from mashumaro.codecs.json import JSONDecoder


class JobConfig(BaseModel):
    """Child object to be nested inside the parent object"""
    job_config_id: str
    config_file_name: Optional[str] = "jobConfig.json"


class SchedulerConfig(BaseModel):
    """The main parent config"""
    input_storage_bucket: str
    cross_account_role_arn: str
    jobs: List[JobConfig]


class SchedulerConfigMapped(BaseModel):
    """The main parent config"""
    input_storage_bucket: str
    cross_account_role_arn: str
    jobs: dict[str, JobConfig]


def test_guessing_of_nested_pydantic():
    # Create a Pydantic model instance
    input_config = SchedulerConfig(
        input_storage_bucket="data_storage_bucket",
        cross_account_role_arn="example-role",
        jobs=[
            JobConfig(
                job_config_id="example-correlation-id-1",
                config_file_name="runConfig.json"
