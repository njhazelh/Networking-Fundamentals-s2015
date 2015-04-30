import logging

__author__ = 'njhazelh'

log = logging.getLogger("Cache")
log.setLevel(logging.DEBUG)

class OriginGetCache:
    def __init__(self):
        self.cache = {}

    def has(self, key):
        return key in self.cache

    def store(self, key, value):
        self.cache[key] = value
        log.debug("%d items in cache", len(self.cache))

    def get(self, key):
        # TODO: Update access time?
        return self.cache[key]
