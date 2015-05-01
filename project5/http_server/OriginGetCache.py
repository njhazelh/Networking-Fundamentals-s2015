import logging
import shelve
from datetime import datetime

__author__ = 'njhazelh'

log = logging.getLogger("Cache")
log.setLevel(logging.DEBUG)

MAX_SIZE = 9 * (2 ** 20) # 9 MB to give a 1MB buffer on the max.

class OriginGetCache:
    def __init__(self):
        self.cache = shelve.open("cdn_cache")
        self.use_times = {} # when each path was last used.
        self.size = 0 # bytes

        # Re-establish use_times if reloading shelve file.
        for key in self.cache.keys():
            self.use_times[key] = datetime.now()
            self.size += len(key) + len(self.cache[key])

    def has(self, key):
        """
        Is key in the cache?
        :param key: The key to check for
        :return: True if there is a value under key in the cache.
        """
        return self.cache.has_key(key)

    def store(self, key, value):
        """
        Store a new key/value pair.  Evicting old entries if needed.
        :param key: The key to add
        :param value: The value to add
        """
        if self.size + len(value) + len(value) > MAX_SIZE:
            self.make_room(key, value)
        self.use_times[key] = datetime.now()
        self.size += len(value)
        self.cache[key] = value
        self.cache.sync()
        log.debug("%d items in cache. %d bytes stored", len(self.cache), self.size)

    def make_room(self, key, value):
        """
        Make room for another value in the cache
        Assumes that the storage for a key-value pair is len(key) + len(value).
        :param key: The key to make room for
        :param value: The value to make room for.
        """
        ordered = sorted(self.use_times, self.use_times.get)
        while self.size + len(key) + len(value) > MAX_SIZE and len(ordered) > 0:
            to_remove = ordered.pop()
            value_to_remove = self.cache[to_remove]
            self.size -= len(to_remove) + len(value_to_remove)
            del self.cache[to_remove]
            del self.use_times[to_remove]
            log.debug("Removed %s from cache", to_remove)

    def get(self, key):
        """
        Get the value stored under key.  Assumes that key is actually in the cache.
        :param key: The key to search under.
        :return: The value under key.
        """
        self.use_times[key] = datetime.now()
        return self.cache[key]
