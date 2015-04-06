import re
import logging

__author__ = 'njhazelh'

COOKIE_PATTERN = re.compile("(.*?)=(.*?);")

log = logging.getLogger("browser")


class CookieCache:
    """
    This class represents a collection of HTTP cookies..
    """

    def __init__(self):
        """
        Initialize the dictionary.
        """
        self.cache = {}

    def set_cookie(self, cookie_str):
        """
        Add a cookie to the cache from a string matching "KEY=VALUE;"
        :param cookie_str: The string containing the cookie to add.
        """
        match = COOKIE_PATTERN.search(cookie_str)
        if match:
            cookie = Cookie(match.group(1), match.group(2))
            log.info("Setting cookie: %s to %s", match.group(1), match.group(2))
            self.add_cookie(cookie)

    def add_cookie(self, cookie):
        """
        Add another cookie to the cache. Overwrite an old cookie if there was already one with
        the same key.
        :param cookie: The cookie to add.
        """
        self.cache[cookie.key] = cookie

    def __iter__(self):
        """
        An iterator method
        :return: yield each of the cookies in no particular order.
        """
        for key in self.cache:
            yield self.cache[key]


    def get_cookie(self, key):
        """
        Get as single cookie.
        :param key: The key of the cookie to get.
        :except: The key may not match a cookie.
        """
        return self.cache[key]


class Cookie:
    """
    This class serves as a named storage until representing a HTTP cookie.
    """

    def __init__(self, key, value):
        """
        Create a cookie. There's more information about
        cookies than modeled here, but we don't use it.
        :param key: The name of the cookie
        :param value: The value of the cookie
        """
        self.key = key
        self.value = value
