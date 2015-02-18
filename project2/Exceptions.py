__author__ = 'njhazelh'


class BadStatusException(Exception):
    pass


class BadHeaderException(Exception):
    pass


class EmptySocketException(Exception):
    pass


class MissingHeaderException(Exception):
    pass


class LockedDomainException(Exception):
    pass


class NoDestinationException(Exception):
    pass


class FailedLoginException(Exception):
    pass
