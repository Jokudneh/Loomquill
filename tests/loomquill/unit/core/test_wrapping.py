from functools import wraps

from flytekit import task, workflow


def test_task_correctly_wrapped():
    @task
    def my_task(a: int) -> int:
        return a

    assert my_task.__wrapped__ == my_task._task_function


def test_stacked_decorators():
    def task_decorator_1(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            print("running task_decorator_1")
            return fn(*args, **kwargs)

        return wrapper

    def task_decorator_2(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            print("running task_decorator_2")
            return fn(*args, **kwargs)

