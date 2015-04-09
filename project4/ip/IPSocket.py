import re
import threading

from ip.IPPacket import IPPacket


__author__ = 'njhazelh'

import socket
import logging
import queue

log = logging.getLogger("ip")

class IPSocket:
    def __init__(self, src_addr):
        self.connected = False
        self.sendSocket = None
        self.recvSocket = None
        self.complete_packets = None
        self.partial_packets = None
        self.thread = None
        self.dest = None
        self.src_addr = src_addr

    def close(self):
        self.recvSocket.close()
        self.sendSocket.close()
        self.connected = False

    def connect(self, dest):
        self.recvSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        self.recvSocket.setblocking(False)
        self.sendSocket = socket.socket(type=socket.SOCK_RAW, proto=socket.IPPROTO_RAW)
        self.sendSocket.connect(dest)

        self.dest = socket.gethostbyname(dest[0])
        self.complete_packets = queue.Queue()
        self.partial_packets = {}
        self.partially_recvd_packet = None

        self.connected = True
        self.thread = threading.Thread(name="ip-loop", target=self.loop)
        self.thread.setDaemon(True)
        self.thread.start()

    def parse_packet(self, packet):
        if packet.dest not in ["127.0.0.1", self.src_addr] or packet.src != self.dest:
            return

        check = packet.checksum()
        if check != 0:
            log.warn("BAD CHECKSUM: %d vs. %s", check, packet.check)

        if packet.fragmentOffset == 0 and packet.flag_more_fragments == 0:
            self.complete_packets.put(packet.data)
        elif packet.flag_more_fragments == 1 and packet.id not in self.partial_packets:
            q = queue.PriorityQueue()
            q.put((packet.fragmentOffset, packet))
            self.partial_packets[packet.id] = q
        else:
            self.partial_packets[packet.id].put((packet.fragmentOffset, packet))
            self.check_packet_is_complete(packet.id)

    def check_packet_is_complete(self, id):
        if id not in self.partial_packets:
            return

        # Check packet is complete
        q = self.partial_packets[id].copy()
        last = 0
        while not q.empty():
            packet = q.get()
            if last != packet.fragmentOffset:
                return
            last += (packet.total_length - packet.header_num_words * 4) / 8

        # Packet must be complete to get here
        data = b''
        q = self.partial_packets[id]
        while not q.empty():
            packet = q.get()
            data += packet.data
        self.complete_packets.put(data)
        del self.partial_packets[id]


    def loop(self):
        log.debug("Started loop thread")
        while self.connected:
            try:
                response = self.recvSocket.recvfrom(65535)
            except OSError as e:
                continue
            bytes, addr = response
            packet = IPPacket.from_network(bytes)
            self.parse_packet(packet)
        log.debug("Ended loop thread")

    def recv(self, max=None):
        if self.partially_recvd_packet is None:
            try:
                packet = self.complete_packets.get(block=False)
            except queue.Empty:
                return None
        else:
            packet = self.partially_recvd_packet

        if max is None or len(packet) <= max:
            recvd = packet
            self.partially_recvd_packet = None
        else:
            recvd = packet[:max]
            self.partially_recvd_packet = packet[max:]

        return recvd

    def has_data(self):
        return self.partially_recvd_packet is not None or \
               not self.complete_packets.empty()

    def wrap_data(self, data):
        p = IPPacket(self.src_addr, self.dest, data)
        return p.to_bytes()

    def send(self, data):
        data = self.wrap_data(data)
        self.sendSocket.send(data)

    def shutdown(self, reason):
        self.recvSocket.shutdown()
        self.sendSocket.shutdown()
        self.close()
