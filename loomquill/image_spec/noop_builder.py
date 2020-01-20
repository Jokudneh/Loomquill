from flytekit.image_spec.image_spec import ImageSpec, ImageSpecBuilder


class NoOpBuilder(ImageSpecBuilder):
    """Noop image builder."""

    builder_type = "noop"
