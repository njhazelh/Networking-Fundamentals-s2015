import math, socket

__author__ = 'Nick'


class Message(object):
    """
    This class serves as an interface for all other Messsage subclasses.
    """

    def do(self, connection):
        raise NotImplementedError("do was not implemented")

    def is_final(self):
        raise NotImplementedError("isFinal was not implemented")


class StatusMessage(Message):
    """
    This class represents the data contained in a Status message from the server.
    Such a message takes the form:
        cs5700spring2015 STATUS [0-1000] {+,-,*,/] [0-1000]\n
    The correct response to this message is the answer to the operation.
        cs5700spring2015 [solution]\n
    """

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    @property
    def answer(self):
        if self.op == "+":
            return self.left + self.right
        elif self.op == "-":
            return self.left - self.right
        elif self.op == "*":
            return self.left * self.right
        elif self.op == "/":
            return math.floor(self.left / self.right)
        else:
            raise Exception("Operation not recognized")

    def is_final(self):
        return False

    def do(self, connection):
        response = "cs5700spring2015 {}\n".format(self.answer)
        connection.sendall(response.encode())


class ByeMessage(Message):
    """
    This class represents the data contained in the Bye message from the server.
    Such a message takes the form:
        cs5700spring2015 [64 byte secret] BYE\n
    The correct response to this is to print the secret and close the connection.
    """

    def __init__(self, secret):
        self.secret = secret

    def is_final(self):
        return True

    def do(self, connection):
        print(self.secret)
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()
