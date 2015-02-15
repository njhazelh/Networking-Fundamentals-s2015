import re

class HttpMessage:
    """
    This class contains the HTTP/1.1 protcol.  To create a method, use the
    static create method, which will create an instance of the message to send.
    To obtain a message object from a string obtained from the server, use
    the parse method.
    """
    def __init__():
        pass

    @staticmethod
    def create(info):
        """
        Create a HTTP/1.1 packet to send to the server
        """
        pass

    @staticmethod
    def parse(msg):
        """
        Create a HTTP/1.1 packet from a message from the server, so
        we can parse it.
        """
        pass
