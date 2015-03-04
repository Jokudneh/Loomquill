.. _contributing:

###########################
Flytekit Contribution Guide
###########################

.. tags:: Contribute, Basic

First off, thank you for thinking about contributing! Below you'll find instructions that will hopefully guide you through how to fix, improve, and extend Flytekit.

Please also take some time to read through the :std:ref:`design guides <design>`, which describe the various parts of Flytekit and should make contributing easier.

*******************
📜 Background
*******************

Below is a listing of the most important packages that comprise the flytekit SDK:

- ``flytekit/core``
  This holds all the core functionality of the new API.
- ``flytekit/types``
  We bundle some special types like ``FlyteFile, FlyteSchema etc`` by default here.
- ``flytekit/extend``
  This is the future home of extension points, and currently serves as the raw documentation for extensions.
- ``flytekit/extras``
  This contains code that we want bundled with Flytekit but not everyone may find useful (for example AWS and GCP
  specific logic).
- ``flytekit/remote``
  This implements the interface to interact with the Flyte service. Think of the code here as the Python-object version of Console.
- ``flytekit/testing``
  is the future home for testing functionality like ``mock`` etc, and currently serves as documentation.
  All test extensions should be imported from here.
- ``flytekit/models``
  Protobuf generated Python code is not terribly user-friendly, so we improve upon those ``flyteidl`` classes here.
- ``plugins``
  is the source of all plugins
- ``flytekit/bin/entrypoint.py``
