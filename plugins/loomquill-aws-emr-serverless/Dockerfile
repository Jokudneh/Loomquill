# Reference worker image for AWS EMR Serverless tasks running in Pythonic
# Spark mode. Script Spark and Hive jobs do not need loomquill on the worker
# and can use the upstream EMR Serverless Spark image directly.
#
# Build:
#   docker build --build-arg VERSION=<loomquill-version> \
#       -t <registry>/emr-serverless-loomquill:<tag> .
ARG EMR_BASE_IMAGE=public.ecr.aws/emr-serverless/spark/emr-7.0.0:latest
FROM ${EMR_BASE_IMAGE}
LABEL org.opencontainers.image.source=https://github.com/jokudneh/loomquill

ARG VERSION

USER root

