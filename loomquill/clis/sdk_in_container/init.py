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
