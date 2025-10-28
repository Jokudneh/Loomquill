import typing

import grpc

from flytekit.clients.grpc_utils.auth_interceptor import _ClientCallDetails


class DefaultMetadataInterceptor(grpc.UnaryUnaryClientInterceptor, grpc.UnaryStreamClientInterceptor):
    def _inject_default_metadata(self, call_details: grpc.ClientCallDetails):
        metadata = [("accept", "application/grpc")]
        if call_details.metadata:
            metadata.extend(list(call_details.metadata))
        new_details = _ClientCallDetails(
            call_details.method,
            call_details.timeout,
