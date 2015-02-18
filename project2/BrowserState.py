from CookieCache import CookieCache

__author__ = "Nick Jones"


class BrowserState:
    """
    This class preserves the state of a series of HTTP interactions.
    Information received from the server, gets stored here and pulled when
    new messages get created.
    """

    def __init__(self):
        self.history = set()
        self.cookies = CookieCache()

    def apply_to(self, msg):
        """
        Add all the cookies and stuff to a new client message
        :param msg:
        :return:
        """
        cookie_string = "; ".join(["{}={}".format(cookie.key, cookie.value) for cookie in self.cookies])
        msg.headers['Cookie'] = cookie_string

    def apply_from(self, msg):
        """
        Add new cookies and stuff from a new message from the server
        :param msg:
        :return:
        """
        for cookie in msg.cookies:
            self.cookies.add_cookie(cookie)

    def get_cookie(self, key):
        return self.cookies.get_cookie(key)

    def visit(self, file):
        self.history.add(file)

    def has_visited(self, file):
        return file in self.history
