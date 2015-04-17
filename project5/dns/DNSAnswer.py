import socket
import struct

from util import domain_to_dns


__author__ = 'njhazelh'


class DNSAnswer:
    def __init__(self, domain, data, ttl, cls, type):
        """
        Initialize this Answer
        :param domain: The domain name this answer is responding to.
        :param data: The answer. Must be an IPv4 address.
        :param ttl: The time in seconds that this can live.
        :param cls: The class of this answer.
        :param type: The type of this answer.
        """
        self.domain = domain
        self.type = type
        self.cls = cls
        self.ttl = ttl
        self.data = data

    def to_bytes(self):
        """
        Convert this answer to bytestring form for the network.
        :return: A DNS Answer formatted bytestring for the network.
        """
        ip = socket.inet_aton(self.data)
        return domain_to_dns(self.domain) + \
               struct.pack("!HHIH", self.type, self.cls, self.ttl, len(ip)) + \
               ip
