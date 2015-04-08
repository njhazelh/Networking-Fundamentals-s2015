from tcp.TCPSocket import *
from http_browser.Exceptions import LockedDomainException
import socket

__author__ = "Nick Jones"

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
        Send the message to the server.
        If the socket does not have a connection to the server, make one.
        If sending the message to the server fails, repeat until it works.
        :param dest: The destination server domain name or ip
        :param msg: A HttpClientMessage to send to the server.
        """
        if self.dest is None or self.dest != dest or self.socket is None:
            self.connect(dest)
        data = str(msg).encode()
        while True:
            sent = self.socket.sendall(data)
            if sent is None:
                break
            else:
                self.connect(dest)


    def connect(self, dest):
        """
        Connect to dest.  Close previous connection if existing.
        :param dest: The destination to open the socket to.
        :except: LockedDomainException if the domain has been locked to something
                 other than dest.
        """
        if self.locked and self.locked_domain != dest:
            raise LockedDomainException(dest)
        else:
            self.close()
            self.socket = socket.socket()#TCPSocket()
            self.socket.connect(dest)
            self.dest = dest

    def close(self):
        """
        Close the socket and set it to None
        """
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def lock_domain(self, domain):
        """
        Lock the domains that this can connect to to "domain"
        :param domain: The only domain that this socket will connect to.
        """
        self.locked = True
        self.locked_domain = domain

    def unlock_domain(self):
        """
        Unlock the domain.
        """
        self.locked = False
        self.locked_domain = None

    def get_socket(self):
        """
        Get the internal socket. This is kinda a hack, but it works well enough for the moment.
        :return: The internal socket.
        """
        return self.socket
