from unittest import TestCase
from UrlEncodedForm import UrlEncodedForm

__author__ = 'njhazelh'

class TestUrlEncodedForm(TestCase):
    def test___str__(self):
        form = UrlEncodedForm({"username": "bob", "password": "123456789"})
        parts = str(form).split("&")
        self.assertTrue("username=bob" in parts)
        self.assertTrue("password=123456789" in parts)

        form = UrlEncodedForm({"user name": "& !@#$%^&*()<>/?;:'\"{[}]\\`~|", "Pass": "a"})
        parts = str(form).split("&")
        self.assertTrue("Pass=a" in parts)
        self.assertTrue(
            "user+name=%26+%21%40%23%24%25%5e%26%2a%28%29%3c%3e%2f%3f%3b%3a%27%22%7b%5b%7d%5d%5c%60%7e%7c" in parts)
