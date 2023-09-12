# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

import configparser

from heropytools.HeroData.Version import Version
from heropytools.Transport.connection import TransportConnection
import heropytools


def _valid_heropytools_version(version_requirement: str):
    """
    Parse and check version strings of the format:
    x.y.z < heropytools <= X.Y.Z
    x.y.z < heropytools
    heropytools <= X.Y.Z
    etc.
    """
    parts = version_requirement.split('<')
    hero_index = [i for i, s in enumerate(parts) if "heropytools" in s][0]

    current_version = Version.from_string(heropytools.__version__)

    pass_lower_check = True
    pass_upper_check = True

    has_lower_check = hero_index == 1
    has_upper_check = hero_index < len(parts) - 1

    if has_lower_check:
        allow_equality = "=" in parts[hero_index]
        lower_limit = Version.from_string(parts[0].strip())
        pass_lower_check = lower_limit <= current_version if allow_equality else lower_limit < current_version

    if has_upper_check:
        allow_equality = "=" in parts[-1]
        upper_limit = Version.from_string(parts[-1].replace("=", "").strip())
        pass_upper_check = current_version <= upper_limit if allow_equality else current_version < upper_limit

    return pass_lower_check and pass_upper_check


def get_server_connection(config_file: str) -> TransportConnection:
    """
    Load information needed to connect to the Hero Server.

    Requires file on the format:
        [Default]
        url=value
        id=value \n

    :param config_file: File containing the information
    :return: Dictionary with the information
    """
    parser = configparser.ConfigParser()
    parser.read(config_file)
    default = parser['Default']

    # Validate that the version of heropytools is adequate
    if not _valid_heropytools_version(default['requirement']):
        raise AssertionError(f"The current version of heropytools '{heropytools.__version__}' does not meet the " +
                             f"requirement: {default['requirement']}")

    return TransportConnection(default['id'], default['url'])


