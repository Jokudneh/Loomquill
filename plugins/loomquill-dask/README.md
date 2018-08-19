# Loomquillkit Dask Plugin

Loomquill can execute `dask` jobs natively on a Kubernetes Cluster, which manages the virtual `dask` cluster's lifecycle
(spin-up and tear down). It leverages the open-source Kubernetes Dask Operator and can be enabled without signing up
for any service. This is like running a transient (ephemeral) `dask` cluster - a type of cluster spun up for a specific
