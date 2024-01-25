import PIL.Image

from flytekit import task, workflow


@task(enable_deck=True)
def t1() -> PIL.Image.Image:
    return PIL.Image.new("L", (100, 100), "black")


@task
def t2(im: PIL.Image.Image) -> PIL.Image.Image:
    return im

