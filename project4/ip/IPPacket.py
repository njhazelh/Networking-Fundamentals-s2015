import socket
import struct

__author__ = 'njhazelh'


def packet_id_gen():
    current = 0
    while True:
        yield current
        current += 1
        current & 0xFF


packet_ids = packet_id_gen()


class IPPacket:
    def __init__(self, src, dest, data, generate=True):
        self.version = 4  # 4  bits
        self.headerLen = 5  # 4  bits
        self.tos = 0  # 1  byte
        # total_length 16 bits

        if generate:
            self.id = next(packet_ids)  # 2  bytes
        else:
            self.id = 0
        self.flags = 0  # 3  bits
        self.fragmentOffset = 0  # 13 bits

        self.ttl = 255  # 1  byte
        self.protocol = 6  # 1  byte
        self.check = 0  # 2  bytes Header checksum 1 1's complement

        self.src = src  # 1  word
        self.dest = dest  # 1  word
        self.options = None  # ?? words
        self.data = data  # ?? bytes

        if generate:
            self.set_checksum()
        else:
            self.check = None

        self.total_length = len(self)

    @classmethod
    def from_network(cls, bytes):
        if len(bytes) < 20:
            return None

        header = struct.unpack("!BBHHHBBH4s4s", bytes[:20])
        result = cls(socket.inet_ntoa(header[8]), socket.inet_ntoa(header[9]), b"", generate=False)
        version_ihl = header[0]
        result.version = version_ihl >> 4
        result.headerLen = version_ihl & 0x0F
        result.tos = header[1]
        result.total_length = header[2]

        if result.total_length != len(bytes): return None

        result.id = header[3]
        flags_fragOffset = header[4]
        result.flags = flags_fragOffset >> 13
        result.fragmentOffset = flags_fragOffset & 0x1FFF
        result.ttl = header[5]
        result.protocol = header[6]
        result.check = header[7]
        if result.headerLen > 20:
            result.options = bytes[20: result.headerLen * 4]
        else:
            result.options = None
        result.data = bytes[result.headerLen * 4:]
        return result

    def __len__(self):
        totalLen = 0
        totalLen += self.headerLen
        totalLen += len(self.data)
        return totalLen

    @property
    def header(self):
        header = struct.pack("!BBHHHBBH4s4s",
                             ((((self.version & 0x0F) << 4) + (self.headerLen & 0x0F))) & 0xFF,
                             self.tos & 0xFF,
                             len(self) & 0xFFFF,
                             self.id & 0xFFFF,
                             (((self.flags & 0x7) << 13) + (self.fragmentOffset & 0x1FFF)) & 0xFFFF,
                             self.ttl & 0xFF,
                             self.protocol & 0xFF,
                             (0 if self.check is None else self.check) & 0xFFFF,
                             socket.inet_aton(self.src),
                             socket.inet_aton(self.dest))
        if self.options is not None:
            # TODO: Check that this works.  It's not really needed, but it's good for robustness.
            optionsLen = self.headerLen - 20
            header = struct.pack("!20s%ds".format(optionsLen), self.options.to_bytes(optionsLen, 'big'))
        return header

    def set_checksum(self):
        check = 0
        i = 0
        header = self.header
        while i < self.headerLen * 4:
            combo = ((header[i] << 8) + header[i + 1])
            check += (combo & 0xFFFF) + (combo >> 16)
            i += 2
        self.check = check
        return check

    def to_bytes(self):
        return self.header + self.data

    def __str__(self):
        labels = [("Version", self.version),
                  ("Header length", self.headerLen),
                  ("TOS", self.tos),
                  ("Total Length", self.total_length),
                  ("ID", self.id),
                  ("Flags", self.flags),
                  ("Offset", self.fragmentOffset),
                  ("TTL", self.ttl),
                  ("Protocol", self.protocol),
                  ("Checksum", self.check),
                  ("Src", self.src),
                  ("Dest", self.dest),
                  ("Options", self.options),
                  ("Data", self.data)]
        string = ""
        for label, val in labels:
            string += label + ": " + str(val) + "\n"

        return string
