.. _design-authoring:

###################
Authoring Structure
###################

.. tags:: Design, Basic

Flytekit's main focus is to provide users with the ability to create their own tasks and workflows.
In this section, we'll take a closer look at how it works under the hood.

*********************
Types and Type Engine
*********************

Flyte uses its own type system, which is defined in the `IDL <https://github.com/flyteorg/flyteidl>`__.
Despite being a dynamic language, Python also has its own type system which is primarily explained in `PEP 484 <https://www.python.org/dev/peps/pep-0484/>`__.
Therefore, Flytekit needs to establish a means of bridging the gap between these two type systems.
This is primariliy accomplished through the use of :py:class:`flytekit.extend.TypeEngine`.
The ``TypeEngine`` works by invoking a series of :py:class:`TypeTransformers <flytekit.extend.TypeTransformer>`.
Each transformer is responsible for providing the functionality that the engine requires for a given native Python type.

*****************
Callable Entities
*****************

The Flyte user experience is built around three main concepts: :ref:`Tasks <divedeep-tasks>`, :ref:`workflows <divedeep-workflows>`, and :ref:`launch plans <divedeep-launchplans>`.
Each of these concepts is supported by one or more Python classes, which are instantiated by decorators (in the case of tasks and workflows) or a regular Python call (in the case of launch plans).

Tasks
=====

Here is the existing hierarchy of task classes:

.. inheritance-diagram:: flytekit.core.python_function_task.PythonFunctionTask flytekit.core.python_function_task.PythonInstanceTask flytekit.extras.sqlite3.task.SQLite3Task
   :top-classes: flytekit.core.base_task.Task
   :parts: 1

For more information on each of the classes, please refer to the corresponding documentation.
