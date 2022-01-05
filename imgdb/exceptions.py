# User defined errors
class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class InputError(Error):
    """Exception raised for errors in the input."""

    name = "InputError"

    def __init__(self, error_ctx):
        self.error_ctx = error_ctx


class ParseError(Error):
    """Exception raised for errors in the configuration file."""

    name = "ParseError"

    def __init__(self, error_ctx):
        self.error_ctx = error_ctx


class ConfigError(Error):
    """Exception raised for empty configuration values."""

    name = "ConfigError"

    def __init__(self, error_ctx):
        self.error_ctx = error_ctx


class ApiError(Error):
    """Exception raised when trying to run the application for the first time without providing API keys."""

    name = "ApiError"

    def __init__(self, error_ctx):
        self.error_ctx = error_ctx
