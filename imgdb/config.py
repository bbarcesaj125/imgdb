import os
from pathlib import Path
import yaml
import click
import logging
from utils import Tcolors
from exceptions import ParseError, ConfigError

# logger("debug")


class Config:
    """Default configuration."""

    # HOME = Path.home()
    HOME = Path("./config_test").resolve()
    XDG_CONFIG_HOME = Path(
        os.getenv("XDG_CONFIG_HOME")
        if os.getenv("XDG_CONFIG_HOME")
        else HOME / ".config"
    )
    XDG_DATA_HOME = Path(
        os.getenv("XDG_DATA_HOME")
        if os.getenv("XDG_DATA_HOME")
        else HOME / ".local/share"
    )
    XDG_CACHE_HOME = Path(
        os.getenv("XDG_CACHE_HOME") if os.getenv("XDG_CACHE_HOME") else HOME / ".cache"
    )
    IMGDB_CONFIG_HOME = Path(XDG_CONFIG_HOME / "imgdb")
    IMGDB_DATA_HOME = Path(XDG_DATA_HOME / "imgdb")
    CONFIG = Path(IMGDB_CONFIG_HOME / "imgdb.yaml")

    DEFAULT_CONFIG = {
        "general": {
            "update frequency": "weekly",
            "log level": "warning",
            "log file path": str(Path(IMGDB_DATA_HOME / "imgdb.log")),
        },
        "interface": {
            "api": {
                "google search api key": "AIzaSyANWkWTK4gmJIRHferGPmqCTdffdIT8XFjhk",
                "imdb custom search id": "32b1e112kdf754be1f",
            }
        },
    }


def check_config_file():
    """This function checks if a config file exists in the CONFIG directory."""

    config_file = Config.CONFIG
    if config_file.is_file():
        return read_config_yaml(config_file)
    else:
        return create_default_yaml(config_file)


def create_default_yaml(config_file):
    """This function creates and saves the default configuration file."""

    config_file_path = config_file
    imgdb_config_dir = Config.IMGDB_CONFIG_HOME

    if not imgdb_config_dir.is_dir():
        try:
            imgdb_config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logging.critical(
                "Something went wrong while trying to create the configuration directory!"
            )
            logging.debug("Error: %s" % e)
            click.echo(
                Tcolors.FAIL
                + "Something went wrong while trying to create the configuration directory!"
                + Tcolors.ENDC
            )
            return 0

    try:
        with open(config_file_path, "w", encoding="utf-8") as config:
            yaml.safe_dump(
                Config.DEFAULT_CONFIG,
                config,
                encoding="utf-8",
                allow_unicode=True,
                default_flow_style=False,
            )
        click.echo(
            Tcolors.OK_GREEN
            + "➜ The configuration file: %s \nhas been created successfully!"
            % config_file_path
            + Tcolors.ENDC
        )
    except Exception as e:
        logging.critical(
            "Something went wrong while trying to save the program's configuration file!"
        )
        logging.debug("Error: %s" % e)
        click.echo(
            Tcolors.FAIL
            + "Something went wrong while trying to save the program's configuration file!"
            + Tcolors.ENDC
        )
        return 0
    return parse_config_yaml(Config.DEFAULT_CONFIG)


def read_config_yaml(config_file):
    """This function extracts configuration options from a YAML configuration file."""

    config_file_path = config_file
    try:
        with open(config_file_path, "r") as config:
            current_config = yaml.safe_load(config)
            logging.debug("Current configuration dictionary: %s" % current_config)
            return parse_config_yaml(current_config)
    except yaml.YAMLError as exc:
        if hasattr(exc, "problem_mark"):
            mark = exc.problem_mark
            logging.critical(
                "The configuration file is malformatted. Error(s) at line %s, column %s!"
                % (mark.line + 1, mark.column + 1)
            )
            click.echo(
                Tcolors.FAIL
                + "The configuration file is malformatted. Error(s) at line %s, column %s!"
                % (mark.line + 1, mark.column + 1)
                + Tcolors.ENDC
            )
        else:
            logging.critical("Failed to parse the configuratiom file!")
            click.echo(
                Tcolors.FAIL + "Failed to parse the configuratiom file!" + Tcolors.ENDC
            )
        return 0
    except Exception as e:
        if hasattr(e, "error_ctx"):
            logging.critical("Error: %s. Context: %s" % (e.name, e.error_ctx))
            click.echo(Tcolors.FAIL + e.error_ctx + Tcolors.ENDC)
        else:
            logging.critical(
                "Something went wrong while trying to read the program's configuration file!"
            )
            logging.debug("Error: %s" % e)
            click.echo(
                Tcolors.FAIL
                + "Something went wrong while trying to read the program's configuration file!"
                + Tcolors.ENDC
            )
        return 0


def parse_config_yaml(current_config):
    """This function parses the configuration values contained in the configuration dictionary obtained by reading the YAML file."""

    config_options = current_config
    used_options = {}

    if config_options is None:
        return validate_config(
            cfg_error=True, cfg_error_ctx="The configuration file cannot be empty!"
        )

    # Aggressively parsing the current configuration options not allowing neither empty nor unknown options
    for key, value in config_options.items():
        if key == "general" and isinstance(value, dict):
            for gen_key, gen_value in config_options[key].items():
                if gen_key == "log file path" and not isinstance(gen_value, dict):
                    used_options[gen_key] = gen_value
                elif gen_key == "download" and not isinstance(gen_value, dict):
                    used_options[gen_key] = gen_value
                elif gen_key == "update frequency" and not isinstance(gen_value, dict):
                    used_options[gen_key] = gen_value
                else:
                    raise ParseError(
                        "Unknown option <%s> in %s section!" % (gen_key, key)
                        if not isinstance(gen_value, dict)
                        else "Invalid value <%s> for option <%s> in '%s' section!"
                        % (gen_value, gen_key, key)
                    )

        elif key == "interface" and isinstance(config_options[key], dict):
            for inter_key, inter_value in value.items():
                if inter_key == "api" and isinstance(inter_value, dict):
                    for api_key, api_value in value[inter_key].items():
                        if api_key == "google search api key" and not isinstance(
                            api_value, dict
                        ):
                            used_options[api_key] = api_value
                        elif api_key == "imdb custom search id" and not isinstance(
                            api_value, dict
                        ):
                            used_options[api_key] = api_value
                        else:
                            raise ParseError(
                                "Unknown option <%s> in %s section!" % (api_key, key)
                                if not isinstance(api_value, dict)
                                else "Invalid value <%s> for option <%s> in '%s' section!"
                                % (api_value, api_key, key)
                            )
                else:
                    raise ParseError(
                        "Unknown option <%s> in '%s' section!" % (inter_key, key)
                    )
        else:
            raise ParseError("Unknown section <%s> in the configuration file!" % key)
    return validate_config(used_options)


def validate_config(config_options={}, cfg_error=None, cfg_error_ctx=None):
    """This function checks if configuration values are not empty or null."""

    if cfg_error and cfg_error_ctx:
        raise ConfigError(cfg_error_ctx)
        return 0

    for key, value in config_options.items():
        try:
            if not value:
                raise ConfigError(
                    "The <%s> option in the configuration file cannot be empty!" % key
                )
        except ConfigError as e:
            logging.critical("Error: %s. Context: %s" % (e.name, e.error_ctx))
            click.echo(Tcolors.FAIL + e.error_ctx + Tcolors.ENDC)
            return 0
    return config_options


if __name__ == "__main__":
    # print(Path(IMGDB_DATA_HOME / "imgdb.log"))
    a = check_config_file()
    print("Returned value is: %s" % a)
    # create_default_yaml(Config.CONFIG)
    print("XDG HOME", Config.XDG_CONFIG_HOME)
    print("XDG DATA HOME", Config.XDG_DATA_HOME)
    print("IMGDB CONFIG HOME", Config.IMGDB_CONFIG_HOME)
    print("IMGDB DATA HOME", Config.IMGDB_DATA_HOME)
    print("CONFIG", Config.CONFIG)
