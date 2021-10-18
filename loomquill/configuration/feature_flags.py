import os


def _get(key: str, default_val: str) -> str:
    v = os.environ.get(key)
    return v if v else default_val
