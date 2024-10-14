from flytekit import lazy_module

why = lazy_module("whylogs")
constraints = lazy_module("whylogs.core.constraints")
pd = lazy_module("pandas")


class WhylogsSummaryDriftRenderer:
    """
    Creates a whylogs' Summary Drift report from two pandas DataFrames. One of them
    is the reference and the other one is the target data, meaning that this is what
    the report will compare it against.
    """

    @staticmethod
