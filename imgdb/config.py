import os
from pathlib import Path
import yaml
import click
import logging
from utils import Tcolors


class Config():
    """ Default configuration. """

    DEFAULT_CONFIG = {
        "general": {
            "update frequency": "weekly",
            "log level": "warning",
            "log file path": ""
        },
        "interface": {
            "api": {
                "google search api key": "AIzaSyANWkWTK4gmJIRHferGPmqCTdffdIT8XFjhk",
                "imdb custom search id": "32b1e112kdf754be1f"
            }
        }
    }

    #HOME = Path.home()
    HOME = Path("./config_test").resolve()
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
        read_config_yaml(config_file)
    else:
        create_default_yaml(config_file)


def create_default_yaml(config_file):
    """ This function creates and saves the default configuration file."""

    config_file_path = config_file
    imgdb_config_dir = Config.IMGDB_CONFIG_HOME

    if not imgdb_config_dir.is_dir():
        try:
            imgdb_config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logging.critical(
                "Something went wrong while trying to create the configuration directory!")
            logging.debug("Error: %s" % e)
            click.echo(Tcolors.FAIL +
                       "Something went wrong while trying to create the configuration directory!" + Tcolors.ENDC)
            return 0

    try:
        with open(config_file_path, "w", encoding="utf-8") as config:
            yaml.safe_dump(Config.DEFAULT_CONFIG, config, encoding="utf-8",
                           allow_unicode=True, default_flow_style=False)
        click.echo(Tcolors.OK_GREEN +
                   "➜ The configuration file: %s \nhas been created successfully!" % config_file_path + Tcolors.ENDC)
    except Exception as e:
        logging.critical(
            "Something went wrong while trying to save the program's configuration file!")
        logging.debug("Error: %s" % e)
        click.echo(Tcolors.FAIL +
                   "Something went wrong while trying to save the program's configuration file!" + Tcolors.ENDC)
        return 0


def read_config_yaml(config_file):
    """ This function extracts configuration options from a YAML configuration file. """

    config_file_path = config_file
    try:
        with open(config_file_path, "r") as config:
            current_config = yaml.safe_load(config)
            print("Current config:", current_config)
            return current_config
    except yaml.YAMLError as exc:
        if hasattr(exc, 'problem_mark'):
            mark = exc.problem_mark
            print("Error position: (%s:%s)" % (mark.line+1, mark.column+1))
    except Exception as e:
        logging.critical(
            "Something went wrong while trying to read the program's configuration file!")
        print(e)
        logging.debug("Error: %s" % e)
        click.echo(Tcolors.FAIL +
                   "Something went wrong while trying to read the program's configuration file!" + Tcolors.ENDC)
        return 0


if __name__ == "__main__":
    check_config_file()
    # create_default_yaml(Config.CONFIG)
    print("XDG HOME", Config.XDG_CONFIG_HOME)
    print("XDG DATA HOME", Config.XDG_DATA_HOME)
    print("IMGDB CONFIG HOME", Config.IMGDB_CONFIG_HOME)
    print("IMGDB DATA HOME", Config.IMGDB_DATA_HOME)
    print("CONFIG", Config.CONFIG)
