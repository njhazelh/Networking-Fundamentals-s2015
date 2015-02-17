__author__ = "Nick Jones"

class BrowserState:
    """
    This class preserves the state of a series of HTTP interactions.
    Information received from the server, gets stored here and pulled when
    new messages get created.
    """
    def __init__(self):
        self.history = []
        self.cookies = []

    def apply_to(self, msg):
        """
        Add all the cookies and stuff to a new client message
        :param msg:
        :return:
        """
        pass

    def apply_from(self, msg):
        """
        Add new cookies and stuff from a new message from the server
        :param msg:
        :return:
        """
        pass

