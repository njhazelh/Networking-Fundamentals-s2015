__author__ = "Nick Jones"


class HttpClientMessage:
    """
    This represents a HTTP/1.1 message from a client to a server.
    """

    DEFAULT_VERSION = "HTTP/1.1"
    DEFAULT_HEADERS = {
        "Host": "cs5700sp15.ccs.neu.edu",
        "User-Agent": "FailSauce/0.1",
    }

    def __init__(self, method, resource, body, headers):
        """
        Create this message
        The content-length header is set automatically to match the body size.
        :param method: The HTTP method to use.
        :param resource: The resource name to get
        :param body: The body of the message if the message is a POST or PUT
        :param headers: The headers for the message.
        :return:
        """
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
        """
        :return: The String representation of this message to send to the server.
        """
        status = "{} {} {}".format(self.method, self.resource, self.version)

        headers = []
        for key in self.headers:
            headers.append("{}: {}".format(key, self.headers[key]))

        return "\r\n".join([status, "\r\n".join(headers), "", self.body]) + "\r\n"
