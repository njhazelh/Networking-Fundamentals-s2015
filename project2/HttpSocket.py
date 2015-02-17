__author__ = "Nick Jones"

MAX_LINE = 16

class HttpSocket:
    """
    This class handles the sending of multiple HTTP/1.1 messages.  The default
    implementation uses a queue that sends the messages in the order the program
    created them.  Other implementations could use a farm of different socket
    threads to send and receive messages in parallel.
    """

    def __init__(self):
        self.socket = None
        self.buffer = []

    def send(self, msg):
        """
        Send the message somehow.
        """
        self.socket.send(str(msg).encode())

    def read_line(self):
        if len(self.buffer) is 0:
            self.buffer.append(self.socket.recv(MAX_LINE))

    def read(self, bytes):
        buffer_size = len(self.buffer)
        amount_to_read = bytes - buffer_size
        remaining = []

        if amount_to_read > 0:
            while amount_to_read is not 0:
                more_data = self.socket.recv(amount_to_read)
                remaining.append(more_data)
                amount_to_read -= len(more_data)
            result = self.buffer + remaining
            self.buffer = []
        else:
            result = self.buffer[:bytes]
            self.buffer = self.buffer[bytes:]

        return result
