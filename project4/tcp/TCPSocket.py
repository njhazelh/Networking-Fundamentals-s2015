import math
import random
import sys

__author__ = 'njhazelh'

from ip.IPSocket import *
from tcp.TCPPacket import *
from tcp.util import *
import threading
import datetime

HOST = get_ip()
TIME_ALPHA = 0.7 # NEW_RTT = ALPHA * OLD_RTT + (1 - ALPHA) * PACKET_RTT

class CONNECTION_STATE:
    NEW = 0
    SYN_SENT = 1
    OPEN = 2
    FIN_SENT = 3
    CLOSED = 4

class TCPSocket:
    def __init__(self):
        self.socket = None
        self.data_send_queue = queue.Queue()
        self.data_recv_queue = queue.Queue()
        self.out_of_order_packets = []
        port = random.randrange(1024, 65536)
        self.src = (HOST, port)
        self.state = CONNECTION_STATE.NEW

    def connect(self, dest):
        if self.state not in [CONNECTION_STATE.CLOSED, CONNECTION_STATE.NEW]:
            return

        # Connection State
        self.socket = IPSocket(HOST)
        self.socket.connect(dest)
        self.dest = (socket.gethostbyname(dest[0]), dest[1])

        # I/O
        self.current_recv_packet = None

        # TCP Algorithm
        self.ss_thresh = float("inf")
        self.congestion_window = 1
        self.dest_window = float('inf')
        self.RTT = None
        self.next_packet = {
            'fin': False,
            'syn': False,
            'ack': False,
            'ack_num': False,
            'seq': 0
        }
        self.packets_in_network = []
        self.seen_sequence_nums = set()
        self.timed_out_packets = []

        # start the thread
        self.thread = threading.Thread(name="tcp-loop", target=self.loop)
        self.thread.setDaemon(True)
        self.thread.start()

    def send(self, data):
        """
        Send some data over the nextwork. The same as sendall.
        :param data: The data to send
        """
        self.data_send_queue.put(data)

    def sendall(self, data):
        """
        Send all the data over the socket.
        """
        self.send(data)

    def recv(self, max_bytes=None):
        """
        Get data from the socket
        :param max_bytes: The maximum number of bytes to read. None means there is not limit, and the
                          socket should read as much as possible.
        """
        if self.current_recv_packet is None:
            packet = None
            while True:
                print("READING IP PACKET")
                packet = self.data_recv_queue.get()
                if int.from_bytes(packet[2:3], 'big') == self.src[1]:
                    break
            if max_bytes is None or len(packet) <= max_bytes:
                return packet
            else:
                self.current_recv_packet = packet[max_bytes:]
                return packet[:max_bytes]
        else:
            packet = self.current_recv_packet[:max_bytes]
            if max_bytes is None or len(packet) == max_bytes:
                self.current_recv_packet = None
            else:
                self.current_recv_packet = self.current_recv_packet[max_bytes:]
            return packet


    def close(self):
        """
        Close the socket
        """
        self.shutdown()
        self.connected = False


    def shutdown(self):
        """
        Sent the shutdown signal to clean up the connection
        """
        self.next_packet['fin'] = True


    #================================================================
    #
    #                     HELPER METHODS
    #
    #================================================================

    def loop(self):
        """
        Thread target for running TCP separate from application.
        """
        syn_packet = TCPPacket.syn((HOST, 0), self.dest)
        syn_packet.set_checksum()
        self.socket.send(syn_packet.to_bytes())
        self.state = CONNECTION_STATE.SYN_SENT

        while self.state != CONNECTION_STATE.CLOSED:
            self.reset_next_packet()
            print("\nGETTING PACKET\n=======================================")
            packet = self.socket.recv()
            print("\nGOT PACKET\n=======================================")
            self.parse_packet(packet)
            print("\nPARSED RESPONSE\n=======================================")
            self.check_timeouts()
            print("\nCHECKED TIMEOUTS\n=======================================")
            self.send_new_packet()
            print("\nSENT NEW PACKETS\n=======================================")


    def reset_next_packet(self):
        self.next_packet['ack'] = False
        self.next_packet['ack_num'] = 0
        self.next_packet['syn'] = False

    def parse_packet(self, packet):
        packet = TCPPacket.from_network(packet, self.src[0], self.dest[0])

        check = packet.checksum()
        if check != 0:
            print("<<<<<<<<<<<<<BAD CHECKSUM>>>>>>>>>>>>>>", check)
            return

        if packet.syn and packet.ack:
            self.state = CONNECTION_STATE.OPEN
            self.next_packet['ack'] = True
            self.next_packet['ack_num'] = 1 + packet.seq
            self.handle_ack(packet)
        elif packet.fin and packet.ack:
            self.state = CONNECTION_STATE.CLOSED
            self.next_packet['ack'] = True
            self.next_packet['ack_num'] = 1 + packet.seq
            self.handle_ack(packet)
        elif packet.fin:
            self.next_packet['fin'] = True
            self.next_packet['ack'] = True
            self.next_packet['ack_num'] = 1 + packet.seq
        elif packet.ack:
            self.handle_ack(packet)
        else:
            self.next_packet['ack'] = True
            self.next_packet['ack_num'] = packet.seq

        if packet.seq not in self.seen_sequence_nums:
            pass
        self.dest_window = packet.window

    def handle_ack(self, packet):
        """
        Handles the ACK clocking part of TCP.
        """
        if self.congestion_window < self.ss_thresh:
            self.congestion_window += 1
        else:
            self.congestion_window += 1 / math.floor(self.congestion_window)

        acked_packets = []
        now = datetime.datetime.now()
        for p in sorted(self.packets_in_network, key=lambda p: p['packet'].seq):
            if p['packet'].seq < p['packet'].ack_num:
                if self.RTT == None:
                    self.RTT = now - p['time_sent'].total_seconds()
                elif not p['timed_out']:
                    packet_rtt = p['time_sent'] - now
                    self.RTT = TIME_ALPHA * self.RTT + (1 - TIME_ALPHA) * packet_rtt.total_seconds() * 1000
                acked_packets.append(p)
        for p in acked_packets:
            self.packets_in_network.remove(p)

    def check_timeouts(self):
        if self.RTT is None:
            return

        timeout_packets = []
        now = datetime.datetime.now()
        for p in self.packets_in_network:
            if now - p.sent_at > 2 * self.RTT:
                timeout_packets.append(p)
                p['timed_out'] = True

        if len(timeout_packets) > 0:
            self.ss_thresh = self.congestion_window / 2
            self.congestion_window = 1
            self.timed_out_packets.extend(timeout_packets)



    def send_new_packet(self):
        print("NEXT PACKET", self.next_packet)
        packet_data =  b''
        packet_size = self.calc_packet_size()
        i = 0
        while not self.data_send_queue.empty() and i < packet_size:
            packet_data += self.data_send_queue.get()
        packet = TCPPacket(self.src, self.dest, self.next_packet['seq'], self.next_packet['ack_num'], packet_data)
        packet.ack = self.next_packet['ack']
        packet.syn = self.next_packet['syn']
        packet.fin = self.next_packet['fin']
        packet.set_checksum()
        self.next_packet['seq'] += max(1, len(packet_data))
        self.packets_in_network.append({
            'packet': packet,
            'time_sent': datetime.datetime.now(),
            'timed_out': False
        })
        print("\nCREATED PACKET\n=======================================")
        print(packet)
        self.socket.send(packet.to_bytes())
        print("\nSENT PACKET\n=======================================")

    def calc_packet_size(self):
        return min(self.congestion_window, self.dest_window)

