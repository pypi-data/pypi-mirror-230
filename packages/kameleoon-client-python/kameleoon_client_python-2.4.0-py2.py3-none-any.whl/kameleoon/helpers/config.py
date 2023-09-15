"""Helper method for reading user configuration file"""

import os
from typing import Any, Dict, Optional

import yaml

from kameleoon.exceptions import ConfigurationNotFoundException
from kameleoon.client_configuration import KameleoonClientConfiguration


def config(
    configuration_path: str = "",
    configuration_object: Optional[KameleoonClientConfiguration] = None,
) -> Dict[str, Any]:
    """This function reads the configuration file."""

    if not os.path.exists(configuration_path) and not configuration_object:
        raise ConfigurationNotFoundException(
            f"No config file {configuration_path} or config object is found"
        )
    config_dict = {}
    if configuration_object:
        config_dict = configuration_object.dict()
    else:
        with open(configuration_path, "r", encoding="utf-8") as yml_file:
            config_dict = yaml.load(yml_file, Loader=yaml.SafeLoader)
    return config_dict
