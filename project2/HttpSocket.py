class HttpSocket:
    """
    This class handles the sending of multiple HTTP/1.1 messages.  The default
    implementation uses a queue that sends the messages in the order the program
    created them.  Other implementations could use a farm of different socket
    threads to send and receive messages in parallel.
    """
    def __init__():
        pass

    def send(msg):
        """
        Send the message somehow.
        """
        pass
