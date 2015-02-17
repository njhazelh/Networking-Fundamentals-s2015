__author__ = "Nick Jones"

from Browser import Browser
from UrlEncodedForm import UrlEncodedForm
from HttpServerMessage import HTTP_STATUS

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
        self.browser.lock_domain("cs5700sp15.ccs.neu.edu")

    def _find_links(self, msg):
        # TODO: Find the links in the html
        return []

    def _parseResponse(self, msg):
        """
        Find all links in the body and add them to the frontier if they're not already there or visited
        """
        if msg.status_code == HTTP_STATUS.OK:
            # Find links and add them to the frontier
            links = self._find_links(msg)
            for link in links:
                if link not in self.frontier and not self.browser.hasVisited(link):
                    self.frontier.append(link)
        elif msg.status_code == HTTP_STATUS.FORBIDDEN:
            # Give up on this resource
            return
        elif msg.status_code == HTTP_STATUS.MOVED_PERM:
            # TODO: add the new link to the frontier
            return
        elif msg.status_code == HTTP_STATUS.FOUND:
            # TODO: Add the next link to the frontier
            return
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
        loggedIn = False

        while not loggedIn:
            self.browser.get("/accounts/login/?next=/fakebook/")
            response = self.browser.getResponse()
            csrf_token = response.get_header('CSRF-TOKEN')
            form = UrlEncodedForm({"username": username,
                                   "password": password,
                                   "csrfmiddlewaretoken": csrf_token})
            headers = {
                "Content-type": "application/x-www-form-urlencoded"
            }
            self.browser.post("/accounts/login/?next=/fakebook/", str(form), headers)
            loginResponse = self.browser.getResponse()
            if loginResponse.status_code == HTTP_STATUS.FOUND:
                loggedIn = True
        self._parseResponse(self.browser.getResponse())


    def run(self, username, password):
        """
        First we need to log into Fakebook and find the initial frontier.
        """
        self._login(username, password)

        while len(self.frontier) is not 0:
            next_resource = self.frontier.pop()
            self.browser.get(next_resource)
            self._parseResponse(self.browser.getResponse())

        self.cleanup()

    def cleanup(self):
        """
        Clean up the algorithm
        """
        self.browser.close()
