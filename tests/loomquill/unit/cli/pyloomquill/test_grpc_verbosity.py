import os


def test_grpc_verbosity_set_on_import():
    """
    Test that GRPC_VERBOSITY is set to NONE if not already present in the environment
    when the SDK container module is imported.
    """
    original_value = os.environ.get("GRPC_VERBOSITY", None)

    try:
        if "GRPC_VERBOSITY" in os.environ:
            del os.environ["GRPC_VERBOSITY"]

        import importlib
