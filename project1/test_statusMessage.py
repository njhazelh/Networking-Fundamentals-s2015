from unittest import TestCase

from messages import StatusMessage


__author__ = 'Nick'


class TestStatusMessage(TestCase):
    def test_fromRegex(self):
        regex = StatusMessage.match("cs5700spring2015 STATUS 3 + 4\n")
        self.assertIsInstance(StatusMessage.fromRegex(regex), StatusMessage)
        self.assertRaises(Exception, StatusMessage.match, None)

    def test_match(self):
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
        self.assertEqual(StatusMessage.fromRegex(StatusMessage.match("cs5700spring2015 STATUS 3 + 4\n")).answer, 7)
        self.assertEqual(StatusMessage.fromRegex(StatusMessage.match("cs5700spring2015 STATUS 13 + 41\n")).answer, 54)
        self.assertEqual(StatusMessage.fromRegex(StatusMessage.match("cs5700spring2015 STATUS 3 * 4\n")).answer, 12)
        self.assertEqual(StatusMessage.fromRegex(StatusMessage.match("cs5700spring2015 STATUS 30 * 4\n")).answer, 120)
        self.assertEqual(StatusMessage.fromRegex(StatusMessage.match("cs5700spring2015 STATUS 3 - 4\n")).answer, -1)
        self.assertEqual(StatusMessage.fromRegex(StatusMessage.match("cs5700spring2015 STATUS 19 - 2\n")).answer, 17)
        self.assertEqual(StatusMessage.fromRegex(StatusMessage.match("cs5700spring2015 STATUS 12 / 4\n")).answer, 3)


    def test_is_final(self):
        self.assertFalse(StatusMessage.fromRegex(StatusMessage.match("cs5700spring2015 STATUS 3 + 4\n")).is_final())
