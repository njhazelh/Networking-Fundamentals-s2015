import struct

from DNSAnswer import DNSAnswer


__author__ = 'njhazelh'


class DNSPacket:
    """
    This class represents a single DNS packet either from the client or from the server.
    It's main functionality is the conversion of human readable data into network-ready
    bytestrings.
    """

    def __init__(self):
        """
        Initialize the data
        :return:
        """
        self.id = 0
        self.is_query = True
        self.opcode = 0
        self.authorative = True
        self.truncate = False
        self.recursive_desired = False
        self.recursive_avail = False
        self.z = 0
        self.response_code = 0
        self.questions = []
        self.answers = []

    def to_bytes(self):
        """
        Convert the data to bytes
        :return: The packet as a network-ready byte-string.
        """
        questions = b''
        answers = b''
        for q in self.questions:
            questions += q.to_bytes()
        for a in self.answers:
            answers += a.to_bytes()

        flags = 0
        flags = flags | self.is_query
        flags = flags << 4
        flags = flags | self.opcode & 0xF
        flags = flags << 1
        flags = flags | self.authorative
        flags = flags << 1
        flags = flags | self.truncate
        flags = flags << 1
        flags = flags | self.recursive_desired
        flags = flags << 1
        flags = flags | self.recursive_avail
        flags = flags << 7
        flags = flags | self.response_code & 0xF

        return struct.pack("!HHHHHH", self.id, flags, len(self.questions), len(self.answers), 0, 0) + \
               questions + \
               answers

    @classmethod
    def from_bytes(cls, bytes):
        """
        Create a DNSPacket from a packet from the network.
        :param bytes: The network packet
        :return: A DNSPacket object containing the same data as bytes.
        """
        packet = cls()
        parts = struct.unpack("!HHHHHH", bytes[:12])
        packet.id = parts[0]
        packet.qr = parts[1] >> 15 == 1
        packet.opcode = (parts[1] >> 11) & 0xF
        packet.authorative = (parts[1] >> 10) & 1 == 1
        packet.truncate = (parts[1] >> 9) & 1 == 1
        packet.recursive_desired = (parts[1] >> 8) & 1 == 1
        packet.recursive_avail = (parts[1] >> 7) & 1 == 1
        packet.z = (parts[1] >> 4) & 0b111
        packet.response_code = parts[1] & 0xF
        return packet

    def add_answer(self, domain, data, ttl=0xFFFF, cls=1, type=1):
        """
        Add an answer to the packet.
        :param domain: The domain the answer is responding to.
        :param data: The answer.
        :param ttl: The time-to-live of the answer in seconds
        :param cls: The class of the answer
        :param type: The type of the answer.
        """
        answer = DNSAnswer(domain, data, ttl, cls, type)
        self.answers.append(answer)

    def __str__(self):
        """
        Convert this object to a human readable string.
        :return: A human readable string.
        """
        string = ""
        pairs = [
            ("ID", self.id),
            ("QR", self.is_query),
            ("OPCODE", self.opcode),
            ("AuthAns", self.authorative),
            ("Trunc", self.truncate),
            ("RD", self.recursive_desired),
            ("RA", self.recursive_avail),
            ("Z", self.z),
            ("RCODE", self.response_code)]
        for pair in pairs:
            string += "%s: %s\n" % pair
        return string
