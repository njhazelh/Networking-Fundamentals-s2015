__author__ = 'njhazelh'


class BadStatusException(Exception):
    """
    This exception represents when a status line in a message from the server is bad.
    """
    pass


class BadHeaderException(Exception):
    """
    This exception represents when a header in a message from the server is malformed.
    """
    pass


class EmptySocketException(Exception):
    """
    This exception represents when a socket has closed, and we try to read from it.
    """
    pass


class MissingHeaderException(Exception):
    """
    This exception represents when we try to get a header from message when the header
    does not exist in the message
    """
    pass


class LockedDomainException(Exception):
    """
    This exception represents when we try to connect a HttpSocket to a domain other
    than the one we have locked it to.
    """
    pass


class NoDestinationException(Exception):
    """
    This exception represents when we try to send a message but we don't name
    as destination server.
    """
    pass


class FailedLoginException(Exception):
    """
    This exception represents when we fail to log into Fakebook for some
    reason.
    """
    pass
