__author__ = 'njhazelh'


class MalformedPacketException(Exception):
    pass

class ClosedSocketException(Exception):
    def __str__(self):
        return "The socket closed for some reason"
