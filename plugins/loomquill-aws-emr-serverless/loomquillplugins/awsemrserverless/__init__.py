"""
.. currentmodule:: flytekitplugins.awsemrserverless

This plugin enables running Spark and Hive jobs on AWS EMR Serverless from
Flyte workflows.  It exposes an async connector that handles the EMR
Serverless job lifecycle (submit, poll, cancel) and a task config type.

.. autosummary::
   :template: custom.rst
   :toctree: generated/

   EMRServerless
   EMRServerlessSparkJobDriver
   EMRServerlessHiveJobDriver
   EMRServerlessTask
