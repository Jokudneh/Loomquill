import subprocess
import re

def run_info_command() -> str:
    """
    Runs the `pyflyte info` command and returns its output.
    """
    out = subprocess.run(
        ["pyflyte", "info"],
        capture_output=True,  # Capture the output streams
        text=True,  # Return outputs as strings (not bytes)
