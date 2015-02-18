__author__ = "Nick Jones"


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

    def __init__(self, method, resource, body, headers):
        self.method = method
        self.resource = resource
        if body is None:
            self.body = ""
        else:
            self.body = body
        self.headers = HttpClientMessage.DEFAULT_HEADERS.copy()
        self.headers.update(headers)
        if body is not None:
            self.headers["Content-length"] = len(body)
        else:
            self.headers["Content-length"] = 0
        self.version = HttpClientMessage.DEFAULT_VERSION

    def __str__(self):
        status = "{} {} {}".format(self.method, self.resource, self.version)

        headers = []
        for key in self.headers:
            headers.append("{}: {}".format(key, self.headers[key]))

        return "\r\n".join([status, "\r\n".join(headers), "", self.body]) + "\r\n"
