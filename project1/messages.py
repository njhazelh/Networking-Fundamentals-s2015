import math
import socket
import re

__author__ = 'Nick'


class Message(object):
    """
    This class serves as an interface for all other Message subclasses.
    """

    @staticmethod
    def model_data(data):
        """
        Take a message in a String and convert it to the appropriate object.
        :param data: The message from the server
        :return: a sub-class of Message representing the data.
        """
        types = [StatusMessage, ByeMessage]

        for type in types:
            result = type.match(data)
            if result is not None:
                return type.from_regex(result)

        raise MessageParseException("Message not recognized:\n\t{}".format(data))

    @classmethod
    def from_regex(cls, regexMatch):
        """
        This method provides a way to construct an instance of this class from
        the result of a regex match.
        """
        raise NotImplementedError("fromRegex was not implemented")

    def do(self, connection):
        """
        React to the message in the appropriate manner.
        :param connection: The socket to reply on.
        """
        raise NotImplementedError("do was not implemented")

    def is_final(self):
        """
        Is this the final message from the server?
        :return: True if this is the final message from the server
        """
        raise NotImplementedError("isFinal was not implemented")


class StatusMessage(Message):
    """
    This class represents the data contained in a Status message from the server.
    Such a message takes the form:
        cs5700spring2015 STATUS [0-1000] {+,-,*,/] [0-1000]\n
    The correct response to this message is the answer to the operation.
        cs5700spring2015 [solution]\n
    """

    PATTERN = re.compile("cs5700spring2015 STATUS (\d+) ([\+,\-,\*,/]) (\d+)\n")

    def __init__(self, left, op, right):
        """
        Constructor using data from an expression. eg. 3 + 45
        :param left: The number on the left of the expression. eg. 3.
        :param op: The operation from the expression. eg. +.
        :param right: The right number from the expression. eg. 45.
        """
        if left < 1 or left > 1000 or right < 1 or right > 1000:
            raise MessageParseException("Numbers in STATUS were out of range (1,1000)")
        self.left = left
        self.op = op
        self.right = right

    @classmethod
    def from_regex(cls, regexMatch):
        """
        Construct an instance of StatusMessage from the result of a match.
        :param regexMatch: The result of a regex match operation.  See match below.
        :return: A StatusMessage object.
        """
        num1 = int(regexMatch.group(1))
        op = regexMatch.group(2)
        num2 = int(regexMatch.group(3))
        return cls(num1, op, num2)

    @staticmethod
    def match(data):
        """
        Match a String to this message type.
        :param data: The data to match against this message.
        :return: None if the message does not match, else a matched object with the
        significant data in groups.
        """
        return StatusMessage.PATTERN.match(data)

    @property
    def answer(self):
        """
        Get the result of expression
        """
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
        """
        This is not a final message
        :return: False
        """
        return False

    def do(self, connection):
        """
        Respond to the message from the server with the solution.
        :param connection: The socket to communicate over.
        """
        response = "cs5700spring2015 {}\n".format(self.answer)
        connection.sendall(response.encode())


class ByeMessage(Message):
    """
    This class represents the data contained in the Bye message from the server.
    Such a message takes the form:
        cs5700spring2015 [64 byte secret] BYE\n
    The correct response to this is to print the secret and close the connection.
    """

    PATTERN = re.compile("cs5700spring2015 ([a-fA-F0-9]+) BYE\n")

    def __init__(self, secret):
        """
        :param secret: The 64-byte secret form the message.
        :return: A ByeMessage representing a message from the server.
        """
        self.secret = secret

    @classmethod
    def from_regex(cls, regexMatch):
        """
        Create an instance of ByeMessage using the data contained in a regex
        match.  See match below.
        :param regexMatch: The match information from the match below.
        :return: An instance of ByeMessage
        """
        return cls(regexMatch.group(1))

    @staticmethod
    def match(data):
        """
        Match a String to this message type and extract the important information.
        Does not expect the secret to be of exact length, because it seemed better to report
        whatever was found.  Secret is expected to be in hexidecimal though.
        :param data: The String to match against.
        :return: A regex match object if the String matches.  Else, None.
        """
        return ByeMessage.PATTERN.match(data)

    def is_final(self):
        """
        This is the final message from the server.
        :return: True
        """
        return True

    def do(self, connection):
        """
        Print out the secret and shutdown the socket connection.
        :param connection: The connection to close.
        """
        print(self.secret)
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()


class MessageParseException(Exception):
    """
    This is an Exception for when the message from the server does
    not match any of the correct formats.
    """
    pass


class EmptyMessageException(Exception):
    """
    This is an Exception for when the message from the server doesn't
    contain anything.  This usually happens when we said something
    wrong.  For example, we answered a STATUS with the incorrect
    solution, or we used an incorrect format.
    """
    pass
