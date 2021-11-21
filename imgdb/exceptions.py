# User defined errors
class Error(Exception):
    """ Base class for exceptions in this module. """
    pass


class InputError(Error):
    """ Exception raised for errors in the input.

    Attributes:
        context -- context in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, context, message):
        self.context = context
        self.message = message
