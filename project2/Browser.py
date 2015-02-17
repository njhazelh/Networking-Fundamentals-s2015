__author__ = 'Nick Jones'

from HttpSocket import HttpSocket
from BrowserState import BrowserState
from HttpClientMessage import HTTP_METHOD, HttpClientMessage
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

    def unlock_domain(self):
        """
        Allow the browser to access resources on all domains.
        """
        self.domain = None

    def request(self, method, file, body=None, headers=None):
        """
        A generic method for making HTTP requests to a server.
        :param method: The HTTP Method
        :param file:
        :param body:
        :param headers:
        :return:
        """
        self.response = None
        message = HttpClientMessage(method, file, body, headers)
        self.socket.send(message)

    def get(self, file, headers={}):
        self.request(HTTP_METHOD.GET, file, None, headers)

    def post(self, file, body=None, headers={}):
        self.request(HTTP_METHOD.POST, file, body, headers)

    def getResponse(self):
        """
        Get the response from the previous message.
        :return:
        """
        if self.response is not None:
            return self.response
        else:
            return HttpServerMessage(self.socket)

    def hasVisited(self, link):
        return link in self.state.history

    def close(self):
        pass
