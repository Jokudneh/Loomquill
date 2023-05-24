.. _design-models:

###########
Model Files
###########

.. tags:: Design, Basic

***********
Description
***********
This section deals with the files in `models <https://github.com/flyteorg/flytekit/tree/master/flytekit/models>`__ folder.
These files are better formatted versions of the generated Python code from `Flyte IDL <https://github.com/flyteorg/flyteidl>`__. In the future, we hope to be able to improve the Python code generator sufficiently to avoid this manual work.

The __only__ reason these files exist is only because the Protobuf generated Python code doesn't work well with IDEs. It doesn't
