from unittest import TestCase

from messages import Message, StatusMessage, ByeMessage, MessageParseException


__author__ = 'Nick'


class TestMessage(TestCase):
    def test_modelData(self):
        self.assertIsInstance(Message.model_data("cs5700spring2015 STATUS 3 + 4\n"), StatusMessage,
                              "Check STATUS message add")
        self.assertIsInstance(Message.model_data("cs5700spring2015 STATUS 3 - 4\n"), StatusMessage,
                              "Check STATUS message sub")
        self.assertIsInstance(Message.model_data("cs5700spring2015 STATUS 3 * 4\n"), StatusMessage,
                              "Check STATUS message mult")
        self.assertIsInstance(Message.model_data("cs5700spring2015 STATUS 12 / 3\n"), StatusMessage,
                              "Check STATUS message div")
        self.assertIsInstance(Message.model_data("cs5700spring2015 abcdef0123456789ABCDEF BYE\n"),
                              ByeMessage, "Check BYE message hexidecimal")
        self.assertRaises(MessageParseException, Message.model_data, "STATUS 3 + 4\n")
        self.assertRaises(MessageParseException, Message.model_data, "cs5700spring201 STATUS 3 + 4\n")
        self.assertRaises(MessageParseException, Message.model_data, "cs5700spring2015 STATUS 3 & 4\n")
        self.assertRaises(MessageParseException, Message.model_data, "cs5700spring2015 STATUS 3 + a\n")
        self.assertRaises(MessageParseException, Message.model_data, "cs5700spring2015 STATUS a + 4\n")
        self.assertRaises(MessageParseException, Message.model_data, "cs5700spring201 STATUS 0 + 4\n")
        self.assertRaises(MessageParseException, Message.model_data, "cs5700spring201 STATUS 3 - 0\n")
        self.assertRaises(MessageParseException, Message.model_data, "cs5700spring201 STATUS 1001 * 4\n")
        self.assertRaises(MessageParseException, Message.model_data, "cs5700spring201 STATUS 3 / 1001\n")
        self.assertRaises(MessageParseException, Message.model_data, "cs5700spring2015 q BYE\n")




