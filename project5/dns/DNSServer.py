import socket

from DNSPacket import DNSPacket


__author__ = 'njhazelh'

UDP_IP = "127.0.0.1"


class DNSServer:
    """
    DNSServer is a simple class to handle CDN server name resolution.
    Is assumes that all packets are querying cs5700cdn.example.com.
    It responds with the http server that will provide the best response time.
    """

    def __init__(self, domain, port):
        """
        Initialize the server.
        :param port: The port the server should listen on.
        """
        self.domain = domain
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((UDP_IP, port))

    def loop(self):
        """
        Run the server loop. Get and respond to packets from clients.
        """
        while True:
            data, address = self.socket.recvfrom(65535)
            response = self.get_response(address, data)
            self.socket.sendto(response.to_bytes(), address)

    def get_response(self, address, data):
        """
        Get the response to send back to the client.
        Currently, this assumes all requests are for cs5700cdn.example.com
        :param data: The message from the client as byte string.
        :return: The message to send to the client as DNSPacket object.
        """
        request = DNSPacket.from_bytes(data)
        response = DNSPacket()
        server_to_use = self.get_best_server(address)
        response.add_answer(self.domain, server_to_use)
        response.id = request.id
        return response

    def get_best_server(self, address):
        """
        Get the best HTTP CDN server available for the client to use.
        :param address: The address of the client
        :return: The IPv4 address of the best HTTP CDN server for the client to use.
        """
        return "127.0.0.1"


