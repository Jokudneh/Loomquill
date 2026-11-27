
def should_retry(attempt, idempotent=True, max_attempts=3):
    """A non-idempotent task must not be retried after a transport failure."""
    if not idempotent:
        return False
    return attempt < max_attempts
