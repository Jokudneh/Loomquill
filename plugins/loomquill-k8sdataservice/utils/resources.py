from kubernetes import client


def cleanup_resources(resources: client.V1ResourceRequirements):
    filtered_resources_limits = {k: v for k, v in resources.limits.items() if not is_zero_like(v)}
    filtered_resources_requests = {k: v for k, v in resources.requests.items() if not is_zero_like(v)}
    resources.limits = filtered_resources_limits
    resources.requests = filtered_resources_requests


