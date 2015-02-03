from unittest import TestCase

from messages import ByeMessage


__author__ = 'Nick'


class TestByeMessage(TestCase):
    def test_fromRegex(self):
        regex = ByeMessage.match("cs5700spring2015 aaaa BYE\n")
        self.assertIsInstance(ByeMessage.fromRegex(regex), ByeMessage)

    def test_match(self):
        # Matches pattern
        match = ByeMessage.match("cs5700spring2015 a BYE\n")
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "a")
        match = ByeMessage.match("cs5700spring2015 abcdef0123456789ABCDEF BYE\n")
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "abcdef0123456789ABCDEF")
        # Did not match
        self.assertIsNone(ByeMessage.match("cs5700spring2015 q BYE\n"))
        self.assertIsNone(ByeMessage.match("cs5700spring2015 a BE\n"))
        self.assertIsNone(ByeMessage.match("cs5700spring2015 a bye\n"))
        self.assertIsNone(ByeMessage.match("cs5700spring201 a BYE\n"))
        self.assertIsNone(ByeMessage.match("cs5700spring2015 a BYE"))

    def test_is_final(self):
        self.assertTrue(ByeMessage.fromRegex(ByeMessage.match("cs5700spring2015 a BYE\n")))
