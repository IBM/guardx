"""Load basic configurations."""

import logging
import os

import yaml

from guardx.schemas import Config

logger = logging.getLogger(__name__)


class ConfigLoader:
    """A configuration loader."""

    @staticmethod
    def load_config(path: str = None) -> Config:
        """Load the SDK configuration from a file path.

        Args:
          path: the configuration path

        Returns:
          The SDK configuration object

        """
        try:
            if path is None:
                path = get_default_config_file_path()
            with open(path) as file:
                config_data = yaml.safe_load(file)
            return Config(**config_data)
        except FileNotFoundError:
            logger.warn(f"Configuration not found at {path}")
            return Config()

    @staticmethod
    def dump_config(path: str, config: Config) -> None:
        """Dumps plugin configuration to a file.

        Args:
          path: configuration file path
          config: the plugin configuration path

        Returns:
          None
        """
        with open(path, "w") as file:
            yaml.safe_dump(config.model_dump(), file)


def get_default_config_file_path() -> str:
    """Returns the path of default config."""
    # TODO Replace to read using importlib resources as impresources
    path_to_current_file = os.path.realpath(__file__)
    current_directory = os.path.dirname(path_to_current_file)
    path = os.path.join(current_directory, "../../resources/config.yaml")
    if not os.path.isfile(path):
        temp = path
        path = os.path.join(current_directory, "../resources/config.yaml")
        logger.debug(f"Configuration not found at {temp}, trying load from {path} (package mode)")
    return path
