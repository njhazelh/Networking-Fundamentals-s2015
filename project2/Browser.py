from Exceptions import LockedDomainException, NoDestinationException, EmptySocketException

__author__ = 'Nick Jones'

from HttpSocket import HttpSocket
from BrowserState import BrowserState
from HttpClientMessage import HttpClientMessage
from HttpServerMessage import HttpServerMessage
import logging

log = logging.getLogger("webcrawler")


class Browser:
    """
    This class acts as an interface for the internet.  Other classes may use it to
    request HTTP resources and get the responses.
    """

    def __init__(self):
        """
        Set up the sockets
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
        log.info("Locked the domain to %s", domain)

    def unlock_domain(self):
        """
        Allow the browser to access resources on all domains.
        """
        self.domain = None
        self.socket.unlock_domain()
        log.info("Unlocked the domain")

    def request(self, method, file, body=None, headers=None, dest=None):
        """
        A generic method for making HTTP requests to a server.
        :param method: The HTTP Method
        :param file: The name of the file to request
        :param body: The body of the request
        :param headers: The headers of the message
        :param dest: The destination of the message
        :return: The response from the server.
        """
        if self.domain is not None and dest is not None and dest != self.domain:
            raise LockedDomainException(dest)
        elif self.domain is not None:
            dest = self.domain
        elif dest is None and self.domain is None:
            log.warn("Missing destination for request")
            raise NoDestinationException()

        self.response = None
        message = HttpClientMessage(method, file, body, headers)
        self.state.apply_to(message)
        self.state.visit(file)
        log.debug("sending %s for %s", method, file)

        while True:
            self.socket.send(dest, message)
            try:
                return self.get_response()
            except EmptySocketException:
                log.warn("Encountered an empty socket")
                continue

    def get(self, file, headers={}, dest=None):
        """
        Send a GET request to the server
        :param file: The file to GET
        :param headers: The headers for the message
        :param dest: The destination of the message
        :return: The response from the server
        """
        return self.request("GET", file, None, headers, dest)

    def post(self, file, body=None, headers={}, dest=None):
        """
        Send a POST request to the server
        :param file: The resource to POST to
        :param body: The body of the message
        :param headers: The headers of the message
        :param dest: The destination of the message
        :return: The response from the server
        """
        return self.request("POST", file, body, headers, dest)

    def get_response(self):
        """
        Get the response from the previous message.
        :return: Get the response from the server.
        """
        if self.response is None:
            self.response = HttpServerMessage(self.socket)
            self.state.apply_from(self.response)
            self.apply_response(self.response)
        return self.response

    def apply_response(self, response):
        """
        Apply the response from the server to the browser.
        :param response: The response from the server
        """
        if response.safe_get_header("connection") == "close":
            self.socket.close()

    def get_cookie(self, key):
        """
        Get a cookie from the BrowserState
        :param key: The key of the cookie
        :return: The cookie under that key
        """
        return self.state.get_cookie(key)

    def has_visited(self, link):
        """
        Have we visited link before?
        :param link: The link to check
        :return: True iff we have visited the link
        """
        return self.state.has_visited(link)

    def close(self):
        """
        Close the browser connections
        """
        self.socket.close()
