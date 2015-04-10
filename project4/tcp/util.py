import socket
import re
import struct
import fcntl
import sys

__author__ = 'njhazelh'


def dump_bytes(bytes):
    print()
    for index, byte in zip(range(1, len(bytes) + 1), bytes):
        sys.stdout.write("%2X " % (byte))
        if index != 0 and index % 4 == 0 or index == len(bytes):
            print("")


def get_ip(ifname='eth0'):
    """
    Get the actual ip address of host.

    gethostbyname(gethostname()) usually returns 127.0.1.1 or
    another loopback address because it's defined in hosts.

    :param ifname: The name of the interface to access.
    :return: The ip address of the host on interface ifname
    """
    ip = socket.gethostbyname(socket.gethostname())
    if re.match("127\.0\.\d*?\.\d*?", ip):
        s = socket.socket()
        data = struct.pack('256s', ifname[:15].encode())
        info = fcntl.ioctl(s.fileno(), 0x8915, data)
        ip = socket.inet_ntoa(info[20:24])
    return ip
