import socket
import struct

__author__ = 'njhazelh'


def packet_id_gen():
    """
    :return: A generator that returns a infinite, cyclic sequence of 16-bit numbers.
    """
    current = 0
    while True:
        yield current
        current += 1
        current = current & 0xFFFF


PACKET_IDS = packet_id_gen()


class IPPacket:
    def __init__(self, src, dest, data, generate=True):
        """
        Create an IP packet
        :param src: The source of the packet. IPv4 address
        :param dest: The destination of the packet. IPv4 address
        :param data: The data to send in the packet
        :param generate: Whether to generate a unique id for this packet.
        :return:
        """
        self.version = 4  # 4  bits
        self.header_num_words = 5  # 4  bits
        self.tos = 0  # 1  byte
        # total_length 16 bits

        if generate:
            self.id = next(PACKET_IDS)  # 2  bytes
        else:
            self.id = 0
        self.flag_reserved = 0
        self.flag_dont_fragment = 0
        self.flag_more_fragments = 0
        self.fragmentOffset = 0  # 13 bits

        self.ttl = 255  # 1  byte
        self.protocol = 6  # 1  byte
        self.check = 0  # 2  bytes Header checksum 1 1's complement

        self.src = src  # 1  word
        self.dest = dest  # 1  word
        self.options = None  # ?? words
        self.data = data  # ?? bytes

        self.total_length = len(self)

    @classmethod
    def from_network(cls, bytes):
        """
        Create an IP packet from bytes received from the network.
        :param bytes: The byte-string to parse into a packet.
        :return: A packet object representing the information in bytes
        """
        if len(bytes) < 20:
            print("Not enough bytes")
            return None

        header = struct.unpack("!BBHHHBBH4s4s", bytes[:20])
        result = cls(socket.inet_ntoa(header[8]), socket.inet_ntoa(header[9]), b"", generate=False)
        version_ihl = header[0]
        result.version = version_ihl >> 4
        result.header_num_words = version_ihl & 0x0F
        result.tos = header[1] & 0xFF
        result.total_length = header[2] & 0xFFFF

        if result.total_length != len(bytes):
            print("Length field doesn't match length")
            return None

        result.id = header[3]
        flags_fragOffset = header[4]
        flags = flags_fragOffset >> 13
        result.flag_reserved = flags & 4
        result.flag_dont_fragment = flags & 2
        result.flag_more_fragments = flags & 1
        result.fragmentOffset = flags_fragOffset & 0x1FFF
        result.ttl = header[5]
        result.protocol = header[6]
        result.check = header[7]
        if result.header_num_words > 5:
            result.options = bytes[20: result.header_num_words * 4]
        else:
            result.options = None
        result.data = bytes[result.header_num_words * 4:]
        return result

    def __len__(self):
        totalLen = 0
        totalLen += self.header_num_words * 4
        totalLen += len(self.data)
        return totalLen * 4

    @property
    def header(self):
        """
        :return: A byte-string representation of the header to send over the network.
        """
        flags = (self.flag_reserved << 2) | (self.flag_dont_fragment << 1) | self.flag_more_fragments
        header = struct.pack("!BBHHHBBH4s4s",
                             ((((self.version & 0x0F) << 4) | (self.header_num_words & 0x0F))) & 0xFF,
                             self.tos & 0xFF,
                             self.total_length & 0xFFFF,
                             self.id & 0xFFFF,
                             (((flags & 0x07) << 13) | (self.fragmentOffset & 0x1FFF)) & 0xFFFF,
                             self.ttl & 0xFF,
                             self.protocol & 0xFF,
                             (0 if self.check is None else self.check) & 0xFFFF,
                             socket.inet_aton(self.src),
                             socket.inet_aton(self.dest))
        if self.options is not None:
            header += self.options
        return header

    @property
    def flags(self):
        """
        :return: A tuple containing the three IP flags (reserved, don't_fragment, more_fragments)
        """
        return (self.flag_reserved, self.flag_dont_fragment, self.flag_more_fragments)

    def to_bytes(self):
        """
        :return: This packet as a byte-string to send over the network
        """
        return self.header + self.data

    def checksum(self):
        """
        :return: The checksum of this packet.
        """
        data = self.header
        return checksum(data)

    def __str__(self):
        """
        Create a String representation of this IP packet.
        :return: A string representing the data in this packet.
        """
        string = ""
        labels = [
            ("Version", self.version),
            ("Header length", self.header_num_words),
            ("TOS", self.tos),
            ("Total Length", self.total_length),
            ("ID", self.id),
            ("Flags", self.flags),
            ("Offset", self.fragmentOffset),
            ("TTL", self.ttl),
            ("Protocol", self.protocol),
            ("Checksum", self.check),
            ("Source", self.src),
            ("Destination", self.dest),
            ("Options", self.options),
            ("Data", self.data)
        ]
        for label, val in labels:
            string += label + ": " + str(val) + "\n"

        return string


def checksum(bytes):
    """
    Generate the ones complement of a byte sequence
    :param bytes: A byte-string to check
    :return: The ones complement checksum of the byte-string
    """
    sum = 0
    count = len(bytes)
    i = 0
    while count > 1:
        # Add all the shorts together
        b = bytes[i:i + 2]
        val = int.from_bytes(b, 'big')
        sum += val
        count -= 2
        i += 2
    if count > 0:
        # Add the last odd byte if there is one
        print(bytes[i])
        sum += bytes[i]
    while (sum >> 16) > 0:
        # Carry the overflow
        sum = (sum & 0xffff) + (sum >> 16)

    # Flip the sum
    return sum ^ 0xFFFF
