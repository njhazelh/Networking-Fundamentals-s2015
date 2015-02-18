import re
import logging
from urllib.parse import urlparse
import sys

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
    and done, the end method cleans things up.
    """

    def __init__(self):
        self.frontier = []
        self.browser = Browser()
        self.browser.lock_domain(DOMAIN)
        self.flags = set()

    def _clean_and_filter_links(self, links):
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

    def _find_links(self, msg):
        found_links = []
        soup = BeautifulSoup(msg.body)
        for a in soup.find_all('a', href=True):
            found_links.append(a['href'])
        return self._clean_and_filter_links(found_links)

    def _find_flags(self, msg):
        soup = BeautifulSoup(msg.body)
        for a in soup.find_all('h2', class_="secret_flag"):
            self._add_flag(a.string)

    def _parseResponse(self, resource, msg):
        """
        Find all links in the body and add them to the frontier if they're not already there or visited
        """
        if msg.status_code == HTTP_STATUS.OK:
            self._find_flags(msg)
            links = self._find_links(msg)
            for link in links:
                if link not in self.frontier and not self.browser.has_visited(link):
                    self.frontier.append(link)
        elif msg.status_code == HTTP_STATUS.MOVED_PERM:
            self.frontier.append(msg.get_header("location"))
        elif msg.status_code == HTTP_STATUS.FOUND:
            self.frontier.append(msg.get_header("location"))
        elif msg.status_code == HTTP_STATUS.SERVER_ERROR:
            self.frontier.append(resource)


    def _login(self, username, password):
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
        """
        self._login(username, password)
        log.info("Logged in with username: %s and password: %s", username, password)

        while len(self.frontier) is not 0 and not self._is_done():
            log.debug("%d sites visited", len(self.frontier))
            next_resource = self.frontier.pop()
            response = self.browser.get(next_resource)
            self._parseResponse(next_resource, response)

        self.cleanup()

    def _add_flag(self, flag):
        result = FLAG_PATTERN.match(flag)
        if result is not None:
            log.info("Added flag %s", result.group(1))
            self.flags.add(result.group(1))

    def _is_done(self):
        return len(self.flags) == 5

    def _print_flags(self):
        sys.stdout.write("\n".join(self.flags))

    def cleanup(self):
        """
        Clean up the algorithm
        """
        self._print_flags()
        self.browser.close()
