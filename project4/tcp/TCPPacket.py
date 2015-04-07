import struct
import socket

__author__ = 'msuk'


class TCPPacket:
    def __init__(self, src, dest, data, generate=True):
        # TCP header fields
        self.src = src
        self.dest = dest
        self.seq = 0
        self.len = len(self)
        self.flag = 0
        self.adwin = socket.htons(5840)
        self.check = 0
        self.urgptr = 0
        self.offset = 5
        self.reserved = 0
        self.protocol = socket.IPPROTO_TCP

        # Control Bits
        self.ack = 0
        self.syn = 1
        self.rst = 0
        self.fin = 0
        self.psh = 1
        self.urg = 0

        # TODO: flags
        self.flag = self.fin + (self.syn << 1) + (self.rst << 2) + (self.psh << 3) + (self.ack << 4) + (self.urg << 5)

    def header(self):
        header = struct.pack('HHLLBBHHH', self.src, self.dest, self.seq, self.ack,
                             self.offset, self.flag, self.adwin, self.check, self.urgptr)
        return header

    def pseudo_header(self):
        """
        Creates a pseudo header
        Used to find the TCP checksum
        """
        pseudo = struct.pack("!4s4sBBH", self.src, self.dest, self.reserved, self.protocol, self.len)
        return pseudo

    def checksum(self):
        sum = 0
        count = len(self.data)

        # TODO: Calculation of TCP Checksum

        sum = (sum >> 16) + (sum & 0xFFFF)
        sum = sum + (sum >> 16)
        return ~sum & 0xFFFF

    def getFlags(self):
        return self.flags

    def setOptions(self):
        pass
