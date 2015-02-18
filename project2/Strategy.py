from Exceptions import FailedLoginException

__author__ = "Nick Jones"

from bs4 import BeautifulSoup
from Browser import Browser
from UrlEncodedForm import UrlEncodedForm
from HttpServerMessage import HTTP_STATUS

DOMAIN = ("cs5700sp15.ccs.neu.edu", 80)

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

    def _find_links(self, msg):
        found_links = []
        soup = BeautifulSoup(msg.body)
        for a in soup.find_all('a'):
            if 'href' in a.attrs:
                found_links.append(a['href'])
        return found_links

    def _find_flags(self, msg):
        # TEMPORARY:  Trying to find secret flags
        # TODO: Make sure flag is not already in secret flags list
        secret_flags = []
        soup = BeautifulSoup(msg)
        for a in soup.find_all('h2'):
            if 'class' in a.attrs:
                if 'secret_flag' in a['class']:
                    # TODO: Store secret flag sequence
                    return
        return

    def _parseResponse(self, msg):
        """
        Find all links in the body and add them to the frontier if they're not already there or visited
        """
        if msg.status_code == HTTP_STATUS.OK:
            # Find links and add them to the frontier
            links = self._find_links(msg)
            for link in links:
                if link not in self.frontier and not self.browser.has_visited(link):
                    self.frontier.append(link)
        elif msg.status_code == HTTP_STATUS.FORBIDDEN:
            # Give up on this resource
            return
        elif msg.status_code == HTTP_STATUS.MOVED_PERM:
            # TODO: add the new link to the frontier
            return
        elif msg.status_code == HTTP_STATUS.FOUND:
            self.frontier.append(msg.get_header("location")) # TODO: clean up this link
        elif msg.status_code == HTTP_STATUS.NOT_FOUND:
            # Move on
            return
        elif msg.status_code == HTTP_STATUS.SERVER_ERROR:
            # TODO: Add the file to the frontier again.
            return
        else:
            # Status not recognized, which isn't surprising
            return


    def _login(self, username, password):
        self.browser.get("/accounts/login/?next=/fakebook/")
        self.browser.get_response()
        csrf_token = self.browser.get_cookie('csrftoken').value
        form = UrlEncodedForm({"username": username,
                               "password": password,
                               "csrfmiddlewaretoken": csrf_token})
        headers = {
            "content-type": "application/x-www-form-urlencoded"
        }
        self.browser.post("/accounts/login/?next=/fakebook/", str(form), headers)
        loginResponse = self.browser.get_response()
        if loginResponse.status_code != HTTP_STATUS.FOUND:
            raise FailedLoginException()

        self._parseResponse(loginResponse)


    def run(self, username, password):
        """
        First we need to log into Fakebook and find the initial frontier.
        """
        self._login(username, password)

        while len(self.frontier) is not 0:
            next_resource = self.frontier.pop()
            self.browser.get(next_resource)
            self._parseResponse(self.browser.get_response())

        self.cleanup()

    def cleanup(self):
        """
        Clean up the algorithm
        """
        self.browser.close()
