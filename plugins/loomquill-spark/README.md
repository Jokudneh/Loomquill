# Loomquillkit Spark Plugin

Loomquill can execute Spark jobs natively on a Kubernetes Cluster, which manages a virtual cluster’s lifecycle, spin-up, and tear down. It leverages the open-sourced Spark On K8s Operator and can be enabled without signing up for any service. This is like running a transient spark cluster — a type of cluster spun up for a specific Spark job and torn down after completion.

To install the plugin, run the following command:

```bash
pip install loomquillplugins-spark
```

To configure Spark in the Loomquill deployment's backend, follow [Step 1](https://docs.loomquill.org/en/latest/deployment/plugins/k8s/index.html#deployment-plugin-setup-k8s), [2](https://docs.loomquill.org/en/latest/loomquillsnacks/examples/k8s_spark_plugin/index.html).

All [examples](https://docs.loomquill.org/en/latest/loomquillsnacks/examples/k8s_spark_plugin/index.html) showcasing execution of Spark jobs using the plugin can be found in the documentation.

## Databricks authentication

The Databricks connector uses PAT authentication by default, preserving the
existing `databricks-token` namespace Secret and
`LOOMQUILL_DATABRICKS_ACCESS_TOKEN` fallback.

OAuth machine-to-machine (M2M) authentication can be enabled on the connector:

```yaml
env:
  - name: LOOMQUILL_DATABRICKS_AUTH_TYPE
    value: oauth_m2m
  - name: DATABRICKS_CLIENT_ID
    value: "<service-principal-client-id>"
  - name: DATABRICKS_CLIENT_SECRET
    valueFrom:
      secretKeyRef:
        name: databricks-connector-oauth
        key: client_secret
```

For per-namespace identities, create a `databricks-oauth` Secret in each
workflow namespace:

```yaml
