import unittest
from unittest.mock import MagicMock, Mock
from config import parse_config_yaml, validate_config, read_config_yaml
from exceptions import ConfigError
from unittest.mock import patch, mock_open


class TestConfig(unittest.TestCase):
    """ Testing the configuration parser in config.py. """

    def setUp(self):
        self.current_config = {'general': {'update frequency': 'weekly', 'log level': 'warning',
                                           'log file path': './rt_movie_cover/config_test/.local/share/imgdb/imgdb.log'},
                               'interface': {'api': {'google search api key': 'AIzaSyANWkWTK4gmJIRHferGPmqCTdffdIT8XFjhk',
                                                     'imdb custom search id': '32b1e112kdf754be1f'}}}

    @patch("config.validate_config")
    def test_parse_config_yaml(self, validate_config):

        validate_config.return_value = {'log file path': './rt_movie_cover/config_test/.local/share/imgdb/imgdb.log',
                                        'log level': 'warning', 'update frequency': 'weekly',
                                        'google search api key': 'AIzaSyANWkWTK4gmJIRHferGPmqCTdffdIT8XFjhk',
                                        'imdb custom search id': '32b1e112kdf754be1f'}
        self.parse_config_yaml = parse_config_yaml(self.current_config)

        self.assertEqual(self.parse_config_yaml, {'log file path': './rt_movie_cover/config_test/.local/share/imgdb/imgdb.log',
                                                  'log level': 'warning', 'update frequency': 'weekly',
                                                  'google search api key': 'AIzaSyANWkWTK4gmJIRHferGPmqCTdffdIT8XFjhk',
                                                  'imdb custom search id': '32b1e112kdf754be1f'}, "Parsing failed!")

    @patch("config.parse_config_yaml")
    def test_read_config_yaml(self, parse_config_yaml):
        yaml_file_mock = ("general:\n"
                          "  log file path: ./config_test/.local/share/imgdb/imgdb.log\n"
                          "  log level: warning\n"
                          "  update frequency: weekly\n"
                          "interface:\n"
                          "  api:\n"
                          "    google search api key: AIzaSyANWkWTK4gmJIRHferGPmqCTdffdIT8XFjhk\n"
                          "    imdb custom search id: 32b1e112kdf754be1f")

        file_path_mock = "path/to/imgdb.yaml"
        parse_config_yaml.return_value = {'log file path': './rt_movie_cover/config_test/.local/share/imgdb/imgdb.log',
                                          'log level': 'warning', 'update frequency': 'weekly',
                                          'google search api key': 'AIzaSyANWkWTK4gmJIRHferGPmqCTdffdIT8XFjhk',
                                          'imdb custom search id': '32b1e112kdf754be1f'}

        with patch("builtins.open", mock_open(read_data=yaml_file_mock)) as file_mock:
            self.reading_mock_file = read_config_yaml(file_path_mock)
            self.assertEqual(self.reading_mock_file, {'log file path': './rt_movie_cover/config_test/.local/share/imgdb/imgdb.log',
                                                      'log level': 'warning', 'update frequency': 'weekly',
                                                      'google search api key': 'AIzaSyANWkWTK4gmJIRHferGPmqCTdffdIT8XFjhk',
                                                      'imdb custom search id': '32b1e112kdf754be1f'}, "Reading YAML failed!")

        file_mock.assert_called_once_with(file_path_mock, "r")
