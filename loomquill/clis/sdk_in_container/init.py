import os
import re
from io import BytesIO
from zipfile import ZipFile

import requests
import rich_click as click


@click.command("init")
@click.option(
    "--template",
    default="basic-template-imagespec",
    help="template folder name to be used in the repo - https://github.com/flyteorg/flytekit-python-template.git",
)
@click.argument("project-name")
def init(template, project_name):
    """
