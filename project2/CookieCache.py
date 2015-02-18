import re
import logging

__author__ = 'njhazelh'

COOKIE_PATTERN = re.compile("(.*?)=(.*?);")

log = logging.getLogger("webcrawler")


class CookieCache:
    """
    This class represents a single HTTP cookie.
    """

    def __init__(self):
        self.cache = {}

    def set_cookie(self, cookie_str):
        match = COOKIE_PATTERN.search(cookie_str)
        if match:
            cookie = Cookie(match.group(1), match.group(2))
            log.info("Setting cookie: %s to %s", match.group(1), match.group(2))
            self.add_cookie(cookie)

    def add_cookie(self, cookie):
        self.cache[cookie.key] = cookie

    def __iter__(self):
        for key in self.cache:
            yield self.cache[key]


    def get_cookie(self, key):
        return self.cache[key]


class Cookie:
    def __init__(self, key, value):
        self.key = key
        self.value = value
