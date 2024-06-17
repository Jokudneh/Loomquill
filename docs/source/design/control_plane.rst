.. _design-control-plane:

###################################################
FlyteRemote: A Programmatic Control Plane Interface
###################################################

.. tags:: Remote, Basic

For those who require programmatic access to the control plane, the :mod:`~flytekit.remote` module enables you to perform
certain operations in a Python runtime environment.

Since this section naturally deals with the control plane, this discussion is only relevant for those who have a Flyte
backend set up and have access to it (a local demo cluster will suffice as well).

*****************************
Creating a FlyteRemote Object
*****************************

The :class:`~flytekit.remote.remote.FlyteRemote` class is the entrypoint for programmatically performing operations in a Python
runtime. It can be initialized by passing in the:

* :py:class:`~flytekit.configuration.Config` object: the parent configuration object that holds all the configuration information to connect to the Flyte backend.
* :py:attr:`~flytekit.remote.remote.FlyteRemote.default_project`: the default project to use when fetching or executing flyte entities.
* :py:attr:`~flytekit.remote.remote.FlyteRemote.default_domain`: the default domain to use when fetching or executing flyte entities.
* :py:attr:`~flytekit.remote.remote.FlyteRemote.file_access`: the file access provider to use for offloading non-literal inputs/outputs.
* ``kwargs``: additional arguments that need to be passed to create ``SynchronousFlyteClient``.

A :class:`~flytekit.remote.remote.FlyteRemote` object can be created in various ways:

Auto
====

The :py:class:`~flytekit.remote.remote.FlyteRemote` class's :py:meth:`~flytekit.remote.remote.FlyteRemote.auto` method can be used to automatically construct the ``Config`` object.

.. code-block:: python

    from flytekit import FlyteRemote

    remote = FlyteRemote.auto()

``auto`` also accepts a ``config_file`` argument, which is the path to the configuration file to use.
The order of precedence that ``auto`` follows is:

* Finds all the environment variables that match the configuration variables.
* If no environment variables are set, it looks for a configuration file at the path specified by the ``config_file`` argument.
* If no configuration file is found, it uses the default values.

Sandbox
=======

The :py:class:`~flytekit.remote.remote.FlyteRemote` class's :py:meth:`~flytekit.remote.remote.FlyteRemote.for_sandbox` method can be used to construct the ``Config`` object, specifically to connect to the Flyte cluster.

.. code-block:: python

    from flytekit import FlyteRemote

    remote = FlyteRemote.for_sandbox()

The initialization is as simple as calling ``for_sandbox()`` on the ``FlyteRemote`` class!
This, by default, uses ``localhost:30081`` as the endpoint, and the default minio credentials.

If the sandbox is in a hosted-like environment, then *port-forward* or *ingress URLs* need to be taken care of.

Any Endpoint
============

The :py:class:`~flytekit.remote.remote.FlyteRemote` class's :py:meth:`~flytekit.remote.remote.FlyteRemote.for_endpoint` method can be used to construct the ``FlyteRemote`` object to connect to a specific endpoint.

.. code-block:: python

    from flytekit import FlyteRemote

    remote = FlyteRemote.for_endpoint(
        endpoint="flyte.example.net",
        default_project="flytesnacks",
        default_domain="development",
    )

The ``for_endpoint`` method also accepts:

* ``insecure``: whether to use insecure connections. Defaults to ``False``.
* ``data_config``: can be used to configure how data is downloaded or uploaded to a specific blob storage like S3, GCS, etc.
* ``config_file``: the path to the configuration file to use.

