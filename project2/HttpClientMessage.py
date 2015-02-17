from enum import Enum

class HTTP_METHOD(Enum):
    """
    This is an enum representing the various HTTP methods
    """
    GET = 1
    POST = 2

class HttpClientMessage:
    """
    This class contains the HTTP/1.1 protocol.  To create a method, use the
    static create method, which will create an instance of the message to send.
    To obtain a message object from a string obtained from the server, use
    the parse method.
    """

    DEFAULT_VERSION = "HTTP/1.1"
    DEFAULT_HEADERS = {
        "Host": "cs5700sp15.ccs.neu.edu",
        "User-Agent": "FailSauce/0.1",
    }

    def __init__(self, method, file, body, headers):
        self.method =  method
        self.file = file
        self.body = body
        self.headers = HttpClientMessage.DEFAULT_HEADERS.copy()
        self.headers.update(headers)
        self.headers["Content-Length"] = len(body)
        self.version = HttpClientMessage.DEFAULT_VERSION

    def __str__(self):
        status = "{} {} {}".format(self.method.name, self.file, self.version)

        headers = []
        for key in self.headers:
            headers.append("{}: {}".format(key, self.headers[key]))

        return "\r\n".join([status, "\r\n".join(headers), "", self.body]) + "\r\n"
