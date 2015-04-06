import re
import threading
from ip.IPPacket import IPPacket

__author__ = 'njhazelh'

import socket
import fcntl, struct

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

HOST = get_ip()

class IPSocket:
    def __init__(self):
        self.destIP = None
        self.connected = False
        self.sendSocket = None
        self.recvSocket = None
        self.bytes = None
        self.thread = None

    def close(self):
        self.recvSocket.close()
        self.sendSocket.close()
        self.connected = False

    def connect(self, dest):
        self.recvSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)

        self.sendSocket = socket.socket(type=socket.SOCK_RAW, proto=socket.IPPROTO_RAW)
        self.sendSocket.connect(dest)

        self.dest = socket.gethostbyname(dest[0])

        self.connected = True
        self.thread = threading.Thread(name="ip-loop", target=self.loop)
        self.thread.start()

    def parse_packet(self, packet):
        print(str(packet))

    def loop(self):
        print("Started loop thread")
        while self.connected:
            response = self.recvSocket.recvfrom(65535, flags=socket.MSG_DONTWAIT)
            if socket.errno == socket.EAGAIN:
                print("asdfasdfasdfasdfasdfasdf")
                continue
            addr, bytes = response
            packet = IPPacket.from_network(bytes)
            self.parse_packet(packet)
        print("Ended loop thread")

    def recv(self, max):
        pass

    def wrap_data(self, data):
        p = IPPacket(HOST, self.dest[0], data)
        return p.to_bytes()

    def send(self, data):
        data = self.wrap_data(data)
        self.sendSocket.send(data)

    def shutdown(self, reason):
        self.recvSocket.shutdown()
        self.sendSocket.shutdown()
        self.close()
