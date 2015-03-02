from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from flytekit import lazy_module

if TYPE_CHECKING:
    import great_tables as gt
    import pandas

    import pandera
else:
    gt = lazy_module("great_tables")
    pandas = lazy_module("pandas")
    pandera = lazy_module("pandera")


@dataclass
class PandasReport:
    summary: pandas.DataFrame
    data_preview: pandas.DataFrame
    schema_error_df: Optional[pandas.DataFrame] = None
    data_error_df: Optional[pandas.DataFrame] = None


SCHEMA_ERROR_KEY = "SCHEMA"
DATA_ERROR_KEY = "DATA"
SCHEMA_ERROR_COLUMNS = ["schema", "column", "error_code", "check", "failure_case", "error"]
DATA_ERROR_COLUMNS = ["schema", "column", "error_code", "check", "index", "failure_case", "error"]
DATA_ERROR_DISPLAY_ORDER = ["column", "error_code", "percent_valid", "check", "failure_cases", "error"]

DATA_PREVIEW_HEAD = 5
FAILURE_CASE_LIMIT = 10
ERROR_COLUMN_MAX_WIDTH = 200


class PandasReportRenderer:
    def __init__(self, title: str = "Pandera Error Report"):
        self._title = title

    def _create_success_report(self, data: "pandas.DataFrame", schema: pandera.DataFrameSchema):
        summary = pandas.DataFrame(
            [
                {"Metadata": "Schema Name", "Value": schema.name},
                {"Metadata": "Shape", "Value": f"{data.shape[0]} rows x {data.shape[1]} columns"},
                {"Metadata": "Total schema errors", "Value": 0},
                {"Metadata": "Total data errors", "Value": 0},
                {"Metadata": "Schema Object", "Value": f"```\n{schema.__repr__()}\n```"},
            ]
        )

        return PandasReport(
            summary=summary,
            data_preview=data.head(DATA_PREVIEW_HEAD),
            schema_error_df=None,
            data_error_df=None,
        )

    @staticmethod
    def _reshape_long_failure_cases(long_failure_cases: "pandas.DataFrame"):
        return (
            long_failure_cases.pivot(
                index=["schema_context", "check", "index"], columns="column", values="failure_case"
            )
            .apply(lambda s: s.to_dict(), axis="columns")
