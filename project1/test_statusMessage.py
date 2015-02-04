from unittest import TestCase
import sys

from messages import StatusMessage, MessageParseException


__author__ = 'Nick'


class TestStatusMessage(TestCase):
    def test_from_regex(self):
        regex = StatusMessage.match("cs5700spring2015 STATUS 3 + 4\n")
        msg = StatusMessage.from_regex(regex)
        self.assertIsInstance(msg, StatusMessage)
        self.assertEqual(msg.left, 3)
        self.assertEqual(msg.op, "+")
        self.assertEqual(msg.right, 4)
        self.assertRaises(MessageParseException, StatusMessage.from_regex,
                          StatusMessage.match("cs5700spring2015 STATUS 0 + 1\n"))
        self.assertRaises(MessageParseException, StatusMessage.from_regex,
                          StatusMessage.match("cs5700spring2015 STATUS 1 + 0\n"))
        self.assertRaises(MessageParseException, StatusMessage.from_regex,
                          StatusMessage.match("cs5700spring2015 STATUS 1001 + 1\n"))
        self.assertRaises(MessageParseException, StatusMessage.from_regex,
                          StatusMessage.match("cs5700spring2015 STATUS 1 + 1001\n"))

        print("\nTesting all possible combos of numbers and ops for STATUS parsing")
        for x in range(1, 1001):
            for y in range(1, 1001):
                for op in ["+", "-", "*", "/"]:
                    sys.stdout.write("Testing: {:4d} {} {:4d}\r".format(x, op, y))
                    match = StatusMessage.match("cs5700spring2015 STATUS {} {} {}\n".format(x, op, y))
                    msg = StatusMessage.from_regex(match)
                    self.assertEqual(msg.left, x)
                    self.assertEqual(msg.right, y)
                    self.assertEqual(msg.op, op)
        print("Finished testing")

    def test_match(self):
        self.assertRaises(Exception, StatusMessage.match, None)
        result = StatusMessage.match("cs5700spring2015 STATUS 3 * 4\n")
        self.assertIsNotNone(result)
        self.assertEqual(result.group(1), "3")
        self.assertEqual(result.group(2), "*")
        self.assertEqual(result.group(3), "4")
        result = StatusMessage.match("cs5700spring2015 STATUS 123 + 43\n")
        self.assertIsNotNone(result)
        self.assertEqual(result.group(1), "123")
        self.assertEqual(result.group(2), "+")
        self.assertEqual(result.group(3), "43")
        result = StatusMessage.match("cs5700spring2015 STATUS 213 - 674\n")
        self.assertIsNotNone(result)
        self.assertEqual(result.group(1), "213")
        self.assertEqual(result.group(2), "-")
        self.assertEqual(result.group(3), "674")
        result = StatusMessage.match("cs5700spring2015 STATUS 3 / 4\n")
        self.assertIsNotNone(result)
        self.assertEqual(result.group(1), "3")
        self.assertEqual(result.group(2), "/")
        self.assertEqual(result.group(3), "4")
        self.assertIsNone(StatusMessage.match("cs5700spring2015 STATUS 3 ^ 4\n"))
        self.assertIsNone(StatusMessage.match("cs5700spring2015 STATUS a + 4\n"))
        self.assertIsNone(StatusMessage.match("cs5700spring2015 STATUS 3 / a\n"))
        self.assertIsNone(StatusMessage.match("cs5700spring2015 STATS 3 / 2\n"))
        self.assertIsNone(StatusMessage.match("cs5700spring2015 status 3 / a\n"))
        self.assertIsNone(StatusMessage.match("cs5700spring2015 STATUS 3 / a"))


    def test_answer(self):
        self.assertEqual(StatusMessage.from_regex(StatusMessage.match("cs5700spring2015 STATUS 3 + 4\n")).answer, 7)
        self.assertEqual(StatusMessage.from_regex(StatusMessage.match("cs5700spring2015 STATUS 13 + 41\n")).answer, 54)
        self.assertEqual(StatusMessage.from_regex(StatusMessage.match("cs5700spring2015 STATUS 3 * 4\n")).answer, 12)
        self.assertEqual(StatusMessage.from_regex(StatusMessage.match("cs5700spring2015 STATUS 30 * 4\n")).answer, 120)
        self.assertEqual(StatusMessage.from_regex(StatusMessage.match("cs5700spring2015 STATUS 3 - 4\n")).answer, -1)
        self.assertEqual(StatusMessage.from_regex(StatusMessage.match("cs5700spring2015 STATUS 19 - 2\n")).answer, 17)
        self.assertEqual(StatusMessage.from_regex(StatusMessage.match("cs5700spring2015 STATUS 12 / 4\n")).answer, 3)


    def test_is_final(self):
        self.assertFalse(StatusMessage.from_regex(StatusMessage.match("cs5700spring2015 STATUS 3 + 4\n")).is_final())
