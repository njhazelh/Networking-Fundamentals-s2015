from unittest import TestCase

from messages import Message, StatusMessage, ByeMessage, MessageParseException


__author__ = 'Nick'


class TestMessage(TestCase):
    def test_modelData(self):
        self.assertIsInstance(Message.modelData("cs5700spring2015 STATUS 3 + 4\n"), StatusMessage,
                              "Check STATUS message add")
        self.assertIsInstance(Message.modelData("cs5700spring2015 STATUS 3 - 4\n"), StatusMessage,
                              "Check STATUS message sub")
        self.assertIsInstance(Message.modelData("cs5700spring2015 STATUS 3 * 4\n"), StatusMessage,
                              "Check STATUS message mult")
        self.assertIsInstance(Message.modelData("cs5700spring2015 STATUS 12 / 3\n"), StatusMessage,
                              "Check STATUS message div")
        self.assertIsInstance(Message.modelData("cs5700spring2015 abcdef0123456789ABCDEF BYE\n"),
                              ByeMessage, "Check BYE message hexidecimal")
        self.assertRaises(MessageParseException, Message.modelData, "STATUS 3 + 4\n")
        self.assertRaises(MessageParseException, Message.modelData, "cs5700spring201 STATUS 3 + 4\n")
        self.assertRaises(MessageParseException, Message.modelData, "cs5700spring2015 STATUS 3 & 4\n")
        self.assertRaises(MessageParseException, Message.modelData, "cs5700spring2015 STATUS 3 + a\n")
        self.assertRaises(MessageParseException, Message.modelData, "cs5700spring2015 STATUS a + 4\n")
        self.assertRaises(MessageParseException, Message.modelData, "cs5700spring201 STATUS 3 + 4")
        self.assertRaises(MessageParseException, Message.modelData, "cs5700spring2015 q BYE\n")




