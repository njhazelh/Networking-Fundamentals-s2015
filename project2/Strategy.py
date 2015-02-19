import re
import logging
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from Exceptions import FailedLoginException
from Browser import Browser
from UrlEncodedForm import UrlEncodedForm
from HttpServerMessage import HTTP_STATUS


__author__ = "Nick Jones"

DOMAIN = ("cs5700sp15.ccs.neu.edu", 80)
FLAG_PATTERN = re.compile("FLAG: ([a-fA-F0-9]{64})")
LOGIN_PAGE = "/accounts/login/?next=/fakebook/"

log = logging.getLogger("webcrawler")


class Strategy:
    """
    This class contains the logic of the web crawler.  The start method
    begins the search algorithm.  Each time a message is received from
    the server is is passed to the do method.  When everything is said
    and done, the cleanup method cleans things up.
    """

    def __init__(self):
        """
        Initialize the strategy
        """
        self.frontier = set()
        self.browser = Browser()
        self.browser.lock_domain(DOMAIN)
        self.flags = set()

    def _clean_and_filter_links(self, links):
        """
        Remove links that are not http or in DOMAIN or on the wrong port.
        :param links: A list or set of the links to clean
        :return: A list of links in DOMAIN on the right port.
        """
        links = list(map(urlparse, links))
        links = list(filter(
            lambda link: link.scheme in ["", "http", "https"] \
                         and (link.port is None or int(link.port) == DOMAIN[1]) \
                         and link.netloc in ["", DOMAIN[0]],
            links
        ))
        cleaned_links = []
        for link in links:
            link_str = link.path
            if link.query != "":
                link_str += "?" + link.query
            if link.fragment != "":
                link_str += "#" + link.fragment
            cleaned_links.append(link_str)
        return cleaned_links

    def _find_links(self, soup):
        """
        Look in the html for links we can follow
        :param soup: A BeautifulSoup4 object containing the html body of a HTTP message.
        :return: A collection of cleaned and filtered links found in the html.
        """
        found_links = set()
        for a in soup.find_all('a', href=True):
            found_links.add(a['href'])
        return self._clean_and_filter_links(found_links)

    def _find_flags(self, soup):
        """
        Look for flags in the body. Add them to the set of flags if found.
        Flags take the form:
            <h2 class='secret_flag' style="color:red">
                FLAG: 64-characters-of-random-alphanumerics
            </h2>"
        :param soup: A BeautifulSoup4 object containing the html body of a HTTP message.
        """
        for a in soup.find_all('h2', attrs={"class": "secret_flag"}):
            self._add_flag(a.string)

    def _parseResponse(self, resource, msg):
        """
        React to a message from the server.
        :param resource: The resource we were looking for on the server.
        :param msg: The server response in a HttpServerMessage
        """
        if msg.status_code == HTTP_STATUS.OK:
            msg_body = BeautifulSoup(msg.body)
            self._find_flags(msg_body)
            links = self._find_links(msg_body)
            for link in links:
                if link not in self.frontier and not self.browser.has_visited(link):
                    self.frontier.add(link)
        elif msg.status_code == HTTP_STATUS.MOVED_PERM or msg.status_code == HTTP_STATUS.FOUND:
            location = msg.get_header("location")
            if location not in self.frontier and not self.browser.has_visited(location):
                self.frontier.add(msg.get_header("location"))
        elif msg.status_code == HTTP_STATUS.SERVER_ERROR:
            self.frontier.add(resource)


    def _login(self, username, password):
        """
        Log into Fakebook
        :param username: The username of the user to log in as.
        :param password: The password of the user to log in as.
        :except: FailedLoginException if the login failed.
        """
        self.browser.get(LOGIN_PAGE)
        csrf_token = self.browser.get_cookie('csrftoken').value
        form = UrlEncodedForm({"username": username,
                               "password": password,
                               "csrfmiddlewaretoken": csrf_token})
        headers = {
            "content-type": "application/x-www-form-urlencoded"
        }
        loginResponse = self.browser.post(LOGIN_PAGE, str(form), headers)
        if loginResponse.status_code != HTTP_STATUS.FOUND:
            raise FailedLoginException()

        self._parseResponse(LOGIN_PAGE, loginResponse)


    def run(self, username, password):
        """
        First we need to log into Fakebook and find the initial frontier.
        :param username: The username of the user to log in as.
        :param password: The password of the user to log in as.
        """
        self._login(username, password)
        log.info("Logged in with username: %s and password: %s", username, password)

        while len(self.frontier) is not 0 and not self._is_done():
            log.debug("%d sites visited", len(self.frontier))
            next_resource = self.frontier.pop()
            response = self.browser.get(next_resource)
            self._parseResponse(next_resource, response)

        if len(self.frontier) is 0:
            log.warn("Crawler emptied the frontier")

        self.cleanup()

    def _add_flag(self, flag):
        """
        Add a flag if it matches the flag pattern and it hasn't been seen before.
        :param flag: The string inside the h2 element. Should match "FLAG: [a-fA-F0-9]{64}"
        """
        result = FLAG_PATTERN.match(flag)
        if result is not None:
            log.info("Added flag %s", result.group(1))
            self.flags.add(result.group(1))

    def _is_done(self):
        """
        Have we found all the flags?
        """
        return len(self.flags) == 5

    def _print_flags(self):
        """
        Print all the flags to the console.
        """
        log.info("Found %s flags:", len(self.flags))
        print("\n".join(self.flags))

    def cleanup(self):
        """
        Clean up the algorithm
        """
        self._print_flags()
        self.browser.close()
