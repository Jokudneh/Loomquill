import sys
from pathlib import Path


def copy_content_to_output(input_path: Path, output_path: Path):
    content = input_path.read_text()
