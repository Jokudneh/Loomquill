from typing import List


class DBTHandledError(Exception):
    """
    DBTHandledError wraps error logs and message from command execution that returns ``exit code 1``.

    Parameters
    ----------
    message : str
        Error message.
    logs : list of str
        Logs produced by the command execution.

    Attributes
    ----------
    message : str
