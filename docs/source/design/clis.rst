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

