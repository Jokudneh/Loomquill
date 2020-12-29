.. _design-execution:

#######################
Execution Time Support
#######################

.. tags:: Design, Basic

Most of the tasks that are written in Flytekit will be Python functions decorated with ``@task`` which turns the body of the function into a Flyte task, capable of being run independently, or included in any number of workflows. The interaction between Flytekit and these tasks do not end once they have been serialized and registered onto the Flyte control plane however. When compiled, the command that will be executed when the task is run is hardcoded into the task definition itself.
