# https://github.com/apache/spark/blob/master/resource-managers/kubernetes/docker/src/main/dockerfiles/spark/bindings/python/Dockerfile
FROM apache/spark-py:v3.4.0
LABEL org.opencontainers.image.source=https://github.com/jokudneh/loomquill

USER 0
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN apt-get update && apt-get install -y wget

ARG VERSION

RUN pip install uv --no-cache-dir \
  && uv pip install --system --no-cache-dir -U loomquillplugins-spark==$VERSION loomquill==$VERSION

RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.4.0/hadoop-aws-3.4.0.jar -P /opt/spark/jars && \
    wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar -P /opt/spark/jars && \
    wget https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.4_2.12/1.4.2/iceberg-spark-runtime-3.4_2.12-1.4.2.jar -P /opt/spark/jars && \
    wget https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-aws-bundle/1.4.2/iceberg-aws-bundle-1.4.2.jar -P /opt/spark/jars

