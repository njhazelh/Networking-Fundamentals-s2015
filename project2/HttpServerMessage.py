__author__ = 'njhazelh'

from enum import Enum

class HTTP_STATUS(Enum):
    OK = 200
    MOVED_PERM = 301
    FOUND = 302
    FORBIDDEN = 403
    NOT_FOUND = 404
    SERVER_ERROR = 500

class HttpServerMessage:

    def __init__(self, sock):
        self.headers = {}
        self.body = ""
        self.status_code = None
        self._getMessage(sock)

    def _getMessage(self, sock):
        """
        Read the headers and body into this structure from the network.
        :param sock: A HttpSocket containing a server response
        """
        # TODO: A lot of fancy reading to get the entire message and nothing more.
        # see https://hg.python.org/cpython/file/2.7/Lib/httplib.py as a reference
        pass

    def get_header(self, key):
        return self.headers[key]

    def get_body(self):
        return self.body

    def get_status_code(self):
        return self.status_code


