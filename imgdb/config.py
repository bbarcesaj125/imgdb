import os
from pathlib import Path
import yaml


class Config():
    """ Default configuration. """

    DEFAULT_CONFIG = {
        "general": {
            "update frequency": "weekly",
            "log level": "warning",
            "log file path": ""
        }
    }

    HOME = Path.home()
    XDG_CONFIG_HOME = Path(os.getenv(
        "XDG_CONFIG_HOME") if os.getenv(
        "XDG_CONFIG_HOME") else HOME / ".config")
    XDG_DATA_HOME = Path(os.getenv(
        "XDG_DATA_HOME") if os.getenv(
        "XDG_DATA_HOME") else HOME / ".local/share")
    IMGDB_CONFIG_HOME = Path(XDG_CONFIG_HOME / "imgdb")
    IMGDB_DATA_HOME = Path(XDG_DATA_HOME / "imgdb")
    CONFIG = Path(IMGDB_CONFIG_HOME / "imgdb.yaml")


def check_config_file():
    """ This function checks if a config file exists in the CONFIG directory. """

    config_file = Config.CONFIG
    print(config_file)
    if config_file.is_file():
        parse_config_yaml(config_file)
    else:
        create_default_yaml(config_file)


def create_default_yaml(config_file):
    """."""
    config_file_path = config_file
    imgdb_config_dir = Config.IMGDB_CONFIG_HOME

    if not imgdb_config_dir.is_dir():
        #imgdb_config_dir.mkdir(parents=True, exist_ok=True)
        print("Creating imgdb config dir!")

    with open("imgdb.yaml", "w", encoding="utf-8",) as f:
        yaml.safe_dump(Config.DEFAULT_CONFIG, f, encoding="utf-8",
                       allow_unicode=True, default_flow_style=False)


if __name__ == "__main__":
    create_default_yaml(Config.CONFIG)
    print("XDG HOME", Config.XDG_CONFIG_HOME)
    print("XDG DATA HOME", Config.XDG_DATA_HOME)
    print("IMGDB CONFIG HOME", Config.IMGDB_CONFIG_HOME)
    print("IMGDB DATA HOME", Config.IMGDB_DATA_HOME)
    print("CONFIG", Config.CONFIG)
