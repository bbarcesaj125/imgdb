# User defined errors
class Error(Exception):
    """ Base class for exceptions in this module. """
    pass


class InputError(Error):
    """ Exception raised for errors in the input. """
    name = "InputError"
