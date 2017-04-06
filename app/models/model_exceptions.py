class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class ErrorRecordExists(Error):
    def __init__(self, attribute, message="Record already exist"):
        self.attribute = attribute
        self.message = message


class ErrorRecordNotExists(Error):
    def __init__(self, attribute, message="Record does not exist"):
        self.attribute = attribute
        self.message = message


class ErrorIncorrectPassword(Error):
    def __init__(self, message="Incorrect password"):
        self.message = message


class ErrorNotSet(Error):
    def __init__(self, attribute, message="Record does not exist"):
        self.attribute = attribute
        self.message = message