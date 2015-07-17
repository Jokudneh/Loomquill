import configparser
import datetime
import typing

from flytekit.configuration.file import ConfigEntry, ConfigFile, LegacyConfigEntry, YamlConfigEntry


class Images(object):
    @staticmethod
    def get_specified_images(cfg: typing.Optional[ConfigFile]) -> typing.Dict[str, str]:
        """
        This section should contain options, where the option name is the friendly name of the image and the corresponding
        value is actual FQN of the image. Example of how the section is structured
        [images]
        my_image1=docker.io/flyte:tag
        # Note that the tag is optional. If not specified it will be the default version identifier specified
        my_image2=docker.io/flyte

        :returns a dictionary of name: image<fqn+version> Version is optional
        """
        images: typing.Dict[str, str] = {}
        if cfg is None:
            return images

        if cfg.legacy_config:
            try:
                image_names = cfg.legacy_config.options("images")
            except configparser.NoSectionError:
                return {}
            if image_names:
                for i in image_names:
                    images[str(i)] = cfg.legacy_config.get("images", i)
            return images
        if cfg.yaml_config:
            return cfg.yaml_config.get("images", images)


class Persistence(object):
    SECTION = "persistence"
    ATTACH_EXECUTION_METADATA = ConfigEntry(LegacyConfigEntry(SECTION, "attach_execution_metadata", bool))
