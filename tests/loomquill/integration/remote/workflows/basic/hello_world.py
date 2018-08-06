"""
Hello World Workflow
--------------------

This simple workflow calls a task that returns "Hello World" and then just sets that as the final output of the workflow.

"""

from flytekit import task, workflow


# You can change the signature of the workflow to take in an argument like this:
# def say_hello(name: str) -> str:
