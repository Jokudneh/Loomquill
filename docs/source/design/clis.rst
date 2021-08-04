.. _design-clis:

###################################
Command Line Interfaces and Clients
###################################

.. tags:: CLI, Basic

Flytekit currently ships with two CLIs, both of which rely on the same client implementation code.

*******
Clients
*******
The client code is located in ``flytekit/clients`` and there are two.

* Similar to the :ref:`design-models` files, but a bit more complex, the ``raw`` one is basically a wrapper around the protobuf generated code, with some handling for authentication in place, and acts as a mechanism for autocompletion and comments.
* The ``friendly`` client uses the ``raw`` client, adds handling of things like pagination, and is structurally more aligned with the functionality and call pattern of the CLI itself.

:py:class:`clients.friendly.SynchronousFlyteClient`

:py:class:`clients.raw.RawSynchronousFlyteClient`

***********************
Command Line Interfaces
***********************

Flytectl
=========

`Flytectl <https://pypi.org/project/yt-flyte-playground-flytectl/>`__ is the general CLI to communicate with the Flyte control plane (FlyteAdmin). Think of this as the ``kubectl`` for Flyte.

Think of this as a network-aware (can talk to FlyteAdmin) but not code-aware (no need to have user code checked out) CLI. In the registration flow, this CLI is responsible for shipping the compiled Protobuf files off to FlyteAdmin.

Pyflyte
========

Unlike ``flytectl``, think of this CLI as code-aware, which is responsible for the serialization (compilation) step in the registration flow. It will parse through the user code, looking for tasks, workflows, and launch plans, and compile them to `protobuf files <https://github.com/flyteorg/flyteidl/blob/0b20c5c99f9e964370d4f4ca663990ed56a14c7c/protos/flyteidl/core/workflow_closure.proto#L11-L18>`__.

.. _pyflyte-run:

What is ``pyflyte run``?
========================

The ``pyflyte run`` command is a light-weight, convenience command that incorporates packaging, registering, and launching a workflow into a single command.

It is not a fully featured production scale mode of operation, because it is designed to be a quick and easy iteration tool to get started with Flyte or test small self-contained scripts. The caveat here is it operates on a single file, and this file will have to contain all the required Flyte entities. Let’s take an example so that you can understand it better.

