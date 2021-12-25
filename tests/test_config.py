import unittest
from config import parse_config_yaml, validate_config, read_config_yaml
from exceptions import ConfigError
from unittest.mock import patch, mock_open


class TestConfig(unittest.TestCase):
    """Testing configuration handlers in config.py."""

    def setUp(self):
        """Mock data."""

        self.current_config = {
            "general": {
                "update frequency": "weekly",
                "log level": "warning",
                "log file path": "./rt_movie_cover/config_test/.local/share/imgdb/imgdb.log",
            },
            "interface": {
                "api": {
                    "google search api key": "AIzaSyANWkWTK4gmJIRHferGPmqCTdffdIT8XFjhk",
                    "imdb custom search id": "32b1e112kdf754be1f",
                }
            },
        }
        self.parsed_config = {
            "log file path": "./rt_movie_cover/config_test/.local/share/imgdb/imgdb.log",
            "log level": "warning",
            "update frequency": "weekly",
            "google search api key": "AIzaSyANWkWTK4gmJIRHferGPmqCTdffdIT8XFjhk",
            "imdb custom search id": "32b1e112kdf754be1f",
        }
        self.yaml_file_content = (
            "general:\n"
            "  log file path: ./config_test/.local/share/imgdb/imgdb.log\n"
            "  log level: warning\n"
            "  update frequency: weekly\n"
            "interface:\n"
            "  api:\n"
            "    google search api key: AIzaSyANWkWTK4gmJIRHferGPmqCTdffdIT8XFjhk\n"
            "    imdb custom search id: 32b1e112kdf754be1f"
        )

    @patch("config.validate_config")
    def test_parse_config_yaml(self, validate_config):

        validate_config.return_value = self.parsed_config
        parsed_yaml = parse_config_yaml(self.current_config)

        self.assertEqual(
            parsed_yaml,
            {
                "log file path": "./rt_movie_cover/config_test/.local/share/imgdb/imgdb.log",
                "log level": "warning",
                "update frequency": "weekly",
                "google search api key": "AIzaSyANWkWTK4gmJIRHferGPmqCTdffdIT8XFjhk",
                "imdb custom search id": "32b1e112kdf754be1f",
            },
            "Parsing failed!",
        )

    @patch("config.parse_config_yaml")
    def test_read_config_yaml(self, parse_config_yaml):

        yaml_file_mock = self.yaml_file_content
        file_path_mock = "path/to/imgdb.yaml"

        parse_config_yaml.return_value = {
            "log file path": "./rt_movie_cover/config_test/.local/share/imgdb/imgdb.log",
            "log level": "warning",
            "update frequency": "weekly",
            "google search api key": "AIzaSyANWkWTK4gmJIRHferGPmqCTdffdIT8XFjhk",
            "imdb custom search id": "32b1e112kdf754be1f",
        }

        with patch("builtins.open", mock_open(read_data=yaml_file_mock)) as file_mock:
            reading_mock_file = read_config_yaml(file_path_mock)
            self.assertEqual(
                reading_mock_file,
                {
                    "log file path": "./rt_movie_cover/config_test/.local/share/imgdb/imgdb.log",
                    "log level": "warning",
                    "update frequency": "weekly",
                    "google search api key": "AIzaSyANWkWTK4gmJIRHferGPmqCTdffdIT8XFjhk",
                    "imdb custom search id": "32b1e112kdf754be1f",
                },
                "Reading YAML failed!",
            )

        file_mock.assert_called_once_with(file_path_mock, "r")

    def test_validate_config(self):

        # Changing the <log level>'s value to an empty string to test validate_config()
        self.parsed_config["log level"] = ""
        wrong_config = self.parsed_config

        self.assertEqual(
            validate_config(wrong_config), 0, "Configuration option cannot be empty!"
        )
