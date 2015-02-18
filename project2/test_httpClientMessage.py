from unittest import TestCase
from HttpClientMessage import HttpClientMessage

__author__ = 'njhazelh'

class TestHttpClientMessage(TestCase):
    def test___str__(self):
        msg = HttpClientMessage("GET", "/file/file1.jpg", "body", {"hello": "world"})
        lines = str(msg).split("\r\n")
        self.assertEqual("GET /file/file1.jpg HTTP/1.1", lines[0])
        self.assertTrue("hello: world" in lines[1:5])
        self.assertTrue("User-Agent: FailSauce/0.1" in lines[1:5])
        self.assertTrue("Host: cs5700sp15.ccs.neu.edu" in lines[1:5])
        self.assertTrue("Content-length: 4" in lines[1:5])
        self.assertEqual("", lines[5])
        self.assertEqual("body", lines[6])
