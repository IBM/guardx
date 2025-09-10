"""This module provides a set of unit tests for guardx configuration."""

from pathlib import Path

import yaml

from guardx.config import get_default_config_file_path
from guardx.guardx import Guardx


def test_get_default_config_file_path():
    path = get_default_config_file_path()

    relative_path = "./resources/config.yaml"
    assert str(Path(relative_path).resolve()) == str(Path(path).resolve()), 'Defaut config path gets wrong path'


# Recursive function to convert any object to a dictionary
def object_to_dict(obj):
    if isinstance(obj, dict):  # If it's already a dictionary, process its items
        return {key: object_to_dict(value) for key, value in obj.items() if value is not None}
    elif hasattr(obj, "__dict__"):  # If it's an object with __dict__, process its attributes
        return {key: object_to_dict(value) for key, value in obj.__dict__.items() if value is not None}
    elif isinstance(obj, (list, tuple, set)):  # If it's a list, tuple, or set, process its elements
        return [object_to_dict(item) for item in obj]
    else:  # Otherwise, return it as is (primitive types, etc.)
        return obj


def test_load_config_with_config_path():
    g = Guardx(config_path="./resources/config.yaml")

    with open("./resources/config.yaml", "r") as file:
        data = yaml.safe_load(file)

        assert object_to_dict(g.config) == data, 'Loads incorrect config data'


def test_load_config_without_config_path():
    g = Guardx()

    with open("./resources/config.yaml", "r") as file:
        data = yaml.safe_load(file)

        assert object_to_dict(g.config) == data, 'Loads incorrect config data'
