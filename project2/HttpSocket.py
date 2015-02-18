__author__ = "Nick Jones"

import socket

from Exceptions import LockedDomainException


class HttpSocket:
    """
    This class handles the sending of multiple HTTP/1.1 messages.  The default
    implementation uses a queue that sends the messages in the order the program
    created them.  Other implementations could use a farm of different socket
    threads to send and receive messages in parallel.
    """

    def __init__(self):
        self.dest = None
        self.socket = None
        self.locked_domain = None
        self.locked = False

    def send(self, dest, msg):
        """
        Send the message somehow.
        """
        if self.dest is None or self.dest != dest:
            self.connect(dest)

        self.socket.send(str(msg).encode())

    def connect(self, dest):
        if self.locked and self.locked_domain != dest:
            raise LockedDomainException(dest)
        elif dest == self.dest:
            return
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(dest)
            self.dest = dest

    def close(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def lock_domain(self, domain):
        self.locked = True
        self.locked_domain = domain

    def unlock_domain(self):
        self.locked = False
        self.locked_domain = None

    def get_socket(self):
        return self.socket
