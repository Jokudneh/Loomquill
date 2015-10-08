import http.server as _BaseHTTPServer
import re
from multiprocessing import Queue as _Queue

from flytekit.clients.auth.auth_client import (
    EndpointMetadata,
    OAuthHTTPServer,
    _create_code_challenge,
    _generate_code_verifier,
    _generate_state_parameter,
)
