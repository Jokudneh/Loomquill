"""
EMR Serverless Pythonic-mode entrypoint script.

This file is the canonical source of the bootstrap script that EMR
Serverless workers execute as ``sparkSubmit.entryPoint`` for Pythonic
tasks (i.e. tasks that do not provide an explicit ``spark_job_driver``).

How it is delivered to EMR
--------------------------

The connector pod:

1. reads this file from its own ``site-packages`` install;
2. computes ``hashlib.sha256(content)[:12]`` and uploads (idempotently)
   to ``s3://<bucket>/flyte/emr-serverless/entrypoint-<hash>.py``;
3. passes that S3 URI as ``StartJobRun.jobDriver.sparkSubmit.entryPoint``.

EMR Serverless then downloads this script onto the Spark driver and
runs it with ``spark-submit``.  ``sys.argv[1:]`` carries the actual
``pyflyte-fast-execute`` (or ``pyflyte-execute``) invocation that
should run inside the worker, plus the fast-registration distribution
arguments.

Why a custom entrypoint at all
------------------------------

EMR Serverless's API requires ``sparkSubmit.entryPoint`` to be a
single Python file URI -- there is no "container as entrypoint"
escape hatch (cf. SageMaker / Batch / ECS, which run the container
itself).  We need a thin shim that:

* downloads the fast-registration tarball from Flyte's blob store,
* invokes ``pyflyte-fast-execute`` with the right resolver arguments,
* converts Flytekit's "exit-0-on-user-error" semantics into a non-zero
  exit so EMR reports ``FAILED`` instead of ``SUCCESS``.

This file deliberately has only ``flytekit`` as a runtime dependency
(specifically ``flytekit.tools.fast_registration.download_distribution``)
because it runs *inside the EMR worker*, not the connector pod.

Editing this file
-----------------

Treat this file as part of the connector's *runtime contract* with
EMR workers, not as plugin internals:

* changes here propagate to every Pythonic-mode job on the next
  connector deploy via the content hash in the S3 key;
* the corresponding unit tests live in ``tests/test_entrypoint.py``
  and exercise this module both as imported Python and as the
  spawned subprocess EMR sees;
* upstream alignment: this is the EMR analogue of
  ``flytetools/flytekitplugins/databricks/entrypoint.py`` --
  same shape, different transport (S3 instead of GitHub).
"""

import os
import signal
import subprocess
import sys

from flytekit.tools.fast_registration import download_distribution
