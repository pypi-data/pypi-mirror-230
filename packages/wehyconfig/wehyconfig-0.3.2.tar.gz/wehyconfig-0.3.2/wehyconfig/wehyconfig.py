"""
The main module for `wehyconfig`.
"""
try:
    import tomllib
except ImportError:
    import tomli as tomllib

from pathlib import Path


def read_config(config_source: str, section="") -> dict:
    """Read the specified configuration file.

    Args:
        config_source (str): A path to either a configuration file or
            a directory containing one or more configuration files.
        section (str): If the config_source is a single file, you can
            specify a section within the configuration file.
    Returns:
        dict: A Python dictionary representation of the configuration file.
    """
    config_path = Path(config_source)
    if config_path.is_dir():
        config_files = _get_config_files(config_path)
        config = {}
        for config_file in config_files:
            config[config_file.stem] = _read_config_file(config_file)
    elif config_path.is_file():
        config = _read_config_file(config_path, section)

    return config


def _get_config_files(config_path: Path()):
    """Private function."""
    return config_path.iterdir()


def _read_config_file(config_file: Path(), section=""):
    """Private function."""
    with open(config_file, "rb") as file:
        config = tomllib.load(file)
    if section:
        config = config[section]
    return config
