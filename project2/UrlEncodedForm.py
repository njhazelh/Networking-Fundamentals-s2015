__author__ = 'njhazelh'

import binascii
import re


def encode(string):
    alphaNumSpace = re.compile("[a-zA-Z0-9 ]")
    string = \
        map(lambda c: "%" +
                      str(binascii.hexlify(c.encode()), "ascii") if not alphaNumSpace.match(c) else c,
            string)
    string = "".join(string)
    string = string.replace(" ", "+")
    return string


class UrlEncodedForm:
    def __init__(self, values):
        self.values = values

    def __str__(self):
        return "&".join(["{}={}".format(encode(key),
                                        encode(self.values[key]))
                         for key in self.values])
