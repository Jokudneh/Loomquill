import shutil
import sys
from pathlib import Path


def copy_directory(input_path: Path, output_path: Path):
    if not input_path.exists() or not input_path.is_dir():
        print(f"Error: {input_path} does not exist or is not a directory.")
        return

    try:
        shutil.copytree(input_path, output_path)
        print(f"Directory {input_path} was successfully copied to {output_path}")
