import HttpMessage, HttpSocket, BrowserState

class Strategy:
    """
    This class contains the logic of the web crawler.  The start method
    begins the search algorithm.  Each time a message is received from
    the server is is passed to the do method.  When everything is said
    and done, the end method cleans things up.
    """
    def __init__():
        self.frontier = []
        self.browser = BrowserState()
        self.connection = HttpSocket()

    def start():
        """
        First we need to log into Fakebook and find the initial frontier.
        """
        pass

    def do(msg):
        """
        Handle each message from the server
        """
        pass
        
    def end():
        """
        Clean up the algorithm
        """
        pass
