class EagerException(Exception):
    """Raised when a node in an eager workflow encounters an error.

    This exception should be used in an {{< py_func_ref `@eager <flytekit.core.task.eager>` >}} workflow function to
    catch exceptions that are raised by tasks or subworkflows.

    ```python
    from flytekit import task
    from flytekit.exceptions.eager import EagerException

    @task
