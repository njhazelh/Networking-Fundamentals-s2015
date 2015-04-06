__author__ = 'njhazelh'

from ip.IPSocket import *
import threading

class TCPSocket:
    def __init__(self):
        self.socket = None
        self.data = []

    def close(self):
        self.connected =  False

    def connect(self, dest):
        self.socket = IPSocket()
        self.socket.connect(dest)
        self.connected = True
        # start the thread
        threading.Thread(target=self.loop)

    def loop(self):
        """
        Thread target for running TCP separate from application.
        """
        while self.connected:
            pass

    def send(self, max):
        data = self.data.pop()
        return data

    def write(self, data):
        self.socket.write(data)

    def shutdown(self, reason):
        """
        Sent the shutdown signal
        :param reason: The reason that the connection is being closed
        """
        pass
