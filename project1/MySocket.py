__author__ = 'Nick'

import socket, ssl

class MySocket:

    def __init__(self, secure, hostname, port):
        self.secure = secure
        self.hostname = hostname
        self.port = port
        self.socket = None
