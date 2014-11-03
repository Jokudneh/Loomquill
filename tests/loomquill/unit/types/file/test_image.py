import PIL.Image

from flytekit import task, workflow


@task(enable_deck=True)
def t1() -> PIL.Image.Image:
