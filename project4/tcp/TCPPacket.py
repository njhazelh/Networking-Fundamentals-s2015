import struct
import socket

from tcp.Exceptions import MalformedPacketException


__author__ = 'njhazelh'


class TCPPacket:
    def __init__(self, src, dest, seq, ack_num=0, data=b''):
        """
            Create a TCP packet according to the following model.
            Model from http://www.freesoft.org/CIE/Course/Section4/8.htm

            0                   1                   2                   3
            0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
           |          Source Port          |       Destination Port        |
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
           |                        Sequence Number                        |
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
           |                    Acknowledgment Number                      |
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
           |  Data |           |U|A|P|R|S|F|                               |
           | Offset| Reserved  |R|C|S|S|Y|I|            Window             |
           |       |           |G|K|H|T|N|N|                               |
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
           |           Checksum            |         Urgent Pointer        |
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
           |                    Options                    |    Padding    |
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
           |                             data                              |
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

           :param src: The source info as a tuple (src_ip, src_port)
           :param dest: The destination info as a tuple (dest_ip, dest_port)
           :param seq: The sequence number of the packet
           :param ack_num: The acknowledgement number of the packet.
           :param data: The data that the packet contains.
        """
        # Word 1
        self.src = src

        # Word 2
        self.dest = dest

        # Word 3
        self.seq = seq
        self.ack_num = ack_num

        # Word 4
        self.data_offset = 5
        self.reserved = 0

        # Control Bits
        self.urg = False
        self.ack = False
        self.psh = False
        self.rst = False
        self.syn = False
        self.fin = False

        self.window = 0xFFFF

        # Word 5
        self.check = 0
        self.urgptr = 0

        # Word 6+
        self.options = []

        # use to store bytes received from network
        self.bytes = None
        self.data = data

    @classmethod
    def from_network(cls, data, src_addr, dest_addr):
        if len(data) < 20:
            raise MalformedPacketException(data)
        header = struct.unpack("!HHLL2sHHH", data[0:20])
        src_port = header[0]
        dest_port = header[1]
        seq = header[2]
        ack_num = header[3]
        dataoffset_rsvd_flags = int.from_bytes(header[4], 'big')
        window = header[5]
        check = header[6]
        urgent_ptr = header[7]

        data_offset = dataoffset_rsvd_flags >> 12
        reserved = (dataoffset_rsvd_flags >> 6) & 0b111111
        flags = dataoffset_rsvd_flags & 0b111111
        urg = (flags >> 5) & 1 == 1
        ack = (flags >> 4) & 1 == 1
        psh = (flags >> 3) & 1 == 1
        rst = (flags >> 2) & 1 == 1
        syn = (flags >> 1) & 1 == 1
        fin = flags & 1 == 1
        packet = cls((src_addr, src_port), (dest_addr, dest_port), seq, ack_num, b'')
        packet.data_offset = data_offset
        packet.reserved = reserved
        packet.urg = urg
        packet.ack = ack
        packet.psh = psh
        packet.rst = rst
        packet.syn = syn
        packet.fin = fin
        packet.window = window
        packet.check = check
        packet.urgptr = urgent_ptr

        packet.set_options_from_bytes(data[20: data_offset * 4])
        packet.data = data[data_offset * 4:]

        packet.bytes = data

        print(packet, "\n")
        return packet

    @classmethod
    def ack(cls, src, dest, seq, ack_num, data=b''):
        packet = cls(src, dest, seq, ack_num, data)
        packet.ack = True
        return packet

    @classmethod
    def syn(cls, src, dest, seq=0):
        packet = cls(src, dest, seq)
        packet.syn = True
        return packet

    @classmethod
    def syn_ack(cls, src, dest, seq, ack_num):
        packet = cls(src, dest, seq, ack_num)
        packet.syn = True
        packet.ack = True
        return packet

    @classmethod
    def fin(cls, src, dest, seq, data=b''):
        packet = cls(src, dest, data=data)
        packet.fin = True
        return packet

    @classmethod
    def fin_ack(cls, src, dest, seq, ack_num, data=b''):
        packet = cls(src, dest, seq, ack_num, data)
        packet.fin = True
        packet.ack = True
        return packet

    @property
    def flags(self):
        flags = 0
        flags = flags | (self.urg << 5)
        flags = flags | (self.ack << 4)
        flags = flags | (self.psh << 3)
        flags = flags | (self.rst << 2)
        flags = flags | (self.syn << 1)
        flags = flags | self.fin
        return flags

    @property
    def header(self):
        dataoffset_resvd_flags = 0
        dataoffset_resvd_flags = dataoffset_resvd_flags | ((self.data_offset & 0b1111) << 12)
        dataoffset_resvd_flags = dataoffset_resvd_flags | (self.flags & 0b111111)
        dataoffset_resvd_flags = dataoffset_resvd_flags.to_bytes(2, 'big')

        header = struct.pack('!HHLL2sHHH',
                             self.src[1], self.dest[1],
                             self.seq,
                             self.ack_num,
                             dataoffset_resvd_flags, self.window,
                             self.check, self.urgptr)
        options = self.generate_options()
        return header + options


    def set_options_from_bytes(self, options_bytes):
        options = []
        index = 0
        offset_bytes = 4 * (self.data_offset - 5)
        while index < offset_bytes:
            byte = options_bytes[index]
            if byte == 0:
                options.append({'kind': 0})
                index += 1
                break
            elif byte == 1:
                options.append({'kind': 1})
                index += 1
            elif byte == 2:
                length = options_bytes[index + 1]
                value = int.from_bytes(options_bytes[index + 2: index + length], 'big')
                option = {'kind': 2, 'length': length, 'value': value}
                options.append(option)
                index += 2 + length
            else:
                pass
        self.options = options


    def generate_options(self):
        if self.data_offset == 5:
            return b''

        options = b''
        for option in self.options:
            if option['kind'] == 0:
                options += b'\x00'
            elif option['kind'] == 1:
                options += b'\x01'
            elif option['kind'] == 2:
                l = option['length']
                options += b'\x02' + l.to_bytes(1, 'big') + option['value'].to_bytes(l - 2, 'big')

        # Add padding to reach a multiple of 4 bytes
        pad_size = 4 - len(options) % 4
        options += (0).to_bytes(pad_size, 'big')

        return options


    @property
    def pseudo_header(self):
        return struct.pack("!4s4sBBH",
                           socket.inet_aton(self.src[0]),
                           socket.inet_aton(self.dest[0]),
                           0, 6, len(self))

    def to_bytes(self):
        bytes = self.header
        bytes += self.data
        return bytes

    def set_checksum(self):
        self.check = self.checksum()

    def checksum(self):
        if self.bytes:
            return checksum(self.pseudo_header + self.bytes)
        else:
            return checksum(self.pseudo_header + self.to_bytes())

    def __len__(self):
        data_len = len(self.data)
        return self.data_offset * 4 + data_len

    def __str__(self):
        string = ""
        info = [
            ("SRC", self.src),
            ("DEST", self.dest),
            ("Sequence Number", self.seq),
            ("Ack Number", self.ack_num),
            ("Data offset", self.data_offset),
            ("Reserved", self.reserved),
            ("URG", self.urg),
            ("ACK", self.ack),
            ("PSH", self.psh),
            ("RST", self.rst),
            ("SYN", self.syn),
            ("FIN", self.fin),
            ("Window", self.window),
            ("Checksum", hex(self.check)),
            ("Urgent Ptr", self.urgptr),
            ("Options", self.options),
            ("data", self.data),
            ("Total length", len(self))]

        for label_value in info:
            string += "%s: %s\n" % label_value

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
        sum += bytes[i] << 8
    while (sum >> 16) > 0:
        # Carry the overflow
        sum = (sum & 0xffff) + (sum >> 16)

    # Flip the sum
    return sum ^ 0xFFFF
