from Exceptions import LockedDomainException, NoDestinationException

__author__ = 'Nick Jones'

from HttpSocket import HttpSocket
from BrowserState import BrowserState
from HttpClientMessage import HttpClientMessage
from HttpServerMessage import HttpServerMessage


class Browser:
    """
    This class acts as an interface for the internet.  Other classes may use it to
    request HTTP resources and get the responses.
    """

    def __init__(self):
        """
        Set up the sockets
        :return:
        """
        self.socket = HttpSocket()
        self.state = BrowserState()
        self.response = None

    def lock_domain(self, domain):
        """
        Prevent the browser from accessing resources on other domains
        :param domain: The domain the browser should be locked to.
        """
        self.domain = domain
        self.socket.lock_domain(domain)

    def unlock_domain(self):
        """
        Allow the browser to access resources on all domains.
        """
        self.domain = None
        self.socket.unlock_domain()

    def request(self, method, file, body=None, headers=None, dest=None):
        """
        A generic method for making HTTP requests to a server.
        :param method: The HTTP Method
        :param file:
        :param body:
        :param headers:
        :return:
        """
        if self.domain is not None and dest is not None and dest != self.domain:
            raise LockedDomainException(dest)
        elif self.domain is not None:
            dest = self.domain
        elif dest is None and self.domain is None:
            raise NoDestinationException()

        self.response = None
        message = HttpClientMessage(method, file, body, headers)
        self.state.apply_to(message)
        self.socket.send(dest, message)

    def get(self, file, headers={}, dest=None):
        self.request("GET", file, None, headers, dest)

    def post(self, file, body=None, headers={}, dest=None):
        self.request("POST", file, body, headers, dest)

    def get_response(self):
        """
        Get the response from the previous message.
        :return:
        """
        if self.response is None:
            self.response = HttpServerMessage(self.socket)
            self.state.apply_from(self.response)
        return self.response

    def get_cookie(self, key):
        return self.state.get_cookie(key)

    def has_visited(self, link):
        return link in self.state.history

    def close(self):
        self.socket.close()
