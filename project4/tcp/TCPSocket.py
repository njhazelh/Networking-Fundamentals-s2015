import random

from tcp.Exceptions import ClosedSocketException


__author__ = 'njhazelh'

from ip.IPSocket import *
from tcp.TCPPacket import *
from tcp.util import *
import threading
import datetime
import time

HOST = get_ip()
TIME_ALPHA = 0.7  # NEW_RTT = ALPHA * OLD_RTT + (1 - ALPHA) * PACKET_RTT


class CONNECTION_STATE:
    NEW = 0
    SYN_SENT = 1
    OPEN = 2
    FIN_SENT = 3
    CLOSED = 4
    RST = 5


class TCPSocket:
    def __init__(self):
        self.socket = None
        self.data_send_queue = queue.Queue()
        self.data_recv_queue = queue.Queue()
        self.out_of_order_packets = []
        self.src = (HOST, random.randrange(1024, 65536))
        self.state = CONNECTION_STATE.NEW
        self.thread = None

    def connect(self, dest):
        if self.thread is not None and self.thread.is_alive():
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
        self.bytes_in_net = 0
        self.RTT = None
        self.MSS = 536
        self.next_packet = {
            'fin': False,
            'syn': False,
            'ack': False,
            'ack_num': False,
            'seq': random.randrange(0, 1 << 32)
        }
        self.current_send_packet = None
        self.packets_in_network = set()
        self.resend_queue = queue.PriorityQueue()

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
        self.check_socket_error()

        if self.current_recv_packet is None:
            packet = None
            while True:
                self.check_socket_error()
                if not self.data_recv_queue.empty():
                    packet = self.data_recv_queue.get(block=False)
                    if int.from_bytes(packet[2:3], 'big') == self.src[1]:
                        breakgit
                    time.sleep(0)
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


    # ================================================================
    #
    # HELPER METHODS
    #
    # ================================================================

    def loop(self):
        """
        Thread target for running TCP separate from application.
        """
        while self.state != CONNECTION_STATE.CLOSED:
            self.print_state()
            self.send_new_packets()
            self.reset_next_packet()

            packet = self.socket.recv()
            if packet is not None:
                self.parse_packet(packet)

            self.check_timeouts()

            # Gotta avoid wakelock
            time.sleep(1.0 / 1000)


    def check_socket_error(self):
        if self.state == CONNECTION_STATE.RST:
            raise ClosedSocketException()

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

        for o in packet.options:
            if o['kind'] == 2 and o['length'] == 4:
                self.MSS = o['value']
                break

        if packet.syn and packet.ack:
            self.handle_ack(packet)
        elif packet.fin and packet.ack:
            self.state = CONNECTION_STATE.CLOSED
            self.handle_ack(packet)
        elif packet.rst:
            self.state = CONNECTION_STATE.RST
            sys.exit()
        elif packet.ack:
            if self.state == CONNECTION_STATE.SYN_SENT:
                self.state = CONNECTION_STATE.OPEN
            self.handle_ack(packet)
        elif packet.fin:
            self.next_packet['fin'] = True
        else:
            pass

        self.dest_window = packet.window

    def handle_ack(self, packet):
        """
        Handles the ACK clocking part of TCP.
        """
        self.next_packet['ack'] = True
        self.next_packet['ack_num'] = packet.seq + 1

        # Increase the congestion window.
        if self.congestion_window < self.ss_thresh:
            self.congestion_window += 1
        else:
            self.congestion_window += 1 / self.congestion_window

        # Increase sequence number to next byte the destination wants.
        if packet.ack_num > self.next_packet['seq']:
            self.next_packet['seq'] = packet.ack_num

        # Find packets that were just acked.
        acked_packets = set(filter(lambda p: p[0].seq < self.next_packet['seq'], self.packets_in_network))

        # Remove them from the packets in the network
        self.packets = self.packets_in_network.difference_update(acked_packets)

        # Manage their RTTs.
        now = datetime.datetime.now()
        for p in acked_packets:
            if not p[2]:
                # Packet didn't time out so it's valid for RTT calculation
                packet_rtt = now - p[1]
                if self.RTT is None:
                    self.RTT = packet_rtt.total_seconds() * 1000
                else:
                    self.RTT = TIME_ALPHA * self.RTT + \
                               (1 - TIME_ALPHA) * packet_rtt.total_seconds() * 1000

        # Remove Bytes from the network
        for p, _, _ in acked_packets:
            self.bytes_in_net -= len(p.to_bytes())


    def check_timeouts(self):
        if self.RTT is None:
            return

        timeout_packets = []
        now = datetime.datetime.now()
        for p in self.packets_in_network:
            dt = (now - p[1]).total_seconds() * 1000
            if dt > 2 * self.RTT:
                self.packets_in_network.remove(p)
                timeout_packets.append(p[0])

        if len(timeout_packets) > 0:
            self.ss_thresh = self.congestion_window / 2
            self.congestion_window = 1

            for p in timeout_packets:
                self.resend_queue.put((p.seq, p))

    def send_new_packets(self):
        while (self.current_resend_packet is not None or not self.resend_queue.empty()) and self.room_for_packet():
            self.resend_packet()

        while not self.data_send_queue.empty() and self.room_for_packet():
            self.send_new_packet()

    def room_for_packet(self):
        return self.calc_packet_size() > 28

    def resend_packet(self):
        pass

    def send_new_packet(self):
        max_packet_size = self.calc_packet_size()

        if max_packet_size < 20:
            return

        # Get data
        if self.state == CONNECTION_STATE.NEW:
            # Start the handshake. Send a SYN
            packet = TCPPacket.syn(self.src, self.dest)
            packet.seq = self.next_packet['seq']
            self.state = CONNECTION_STATE.SYN_SENT

        elif self.state == CONNECTION_STATE.SYN_SENT and self.next_packet['ack']:
            # Send an ACK to their SYN_ACK
            seq = self.next_packet['seq']
            packet = TCPPacket.ack(self.src, self.dest, seq, self.next_packet['ack_num'])
            self.state = CONNECTION_STATE.OPEN

        elif self.state == CONNECTION_STATE.OPEN:
            # Send a packet of data or ack another packet.
            packet_size = self.MSS
            if not self.next_packet['ack'] and self.data_send_queue.empty():
                return

            packet_data = b''
            i = 0
            while not self.data_send_queue.empty() and i < packet_size:
                packet_data += self.data_send_queue.get()

            # Create packet
            packet = TCPPacket(self.src,
                               self.dest,
                               self.next_packet['seq'],
                               self.next_packet['ack_num'],
                               packet_data)

            # Configure packet
            packet.ack = self.next_packet['ack']
            packet.syn = self.next_packet['syn']
            packet.fin = self.next_packet['fin']
        else:
            print("SKIPPING SEND", self.state)
            return

        packet.set_checksum()
        packet_bytes = packet.to_bytes()

        # Track that we're sending this packet.
        self.packets_in_network.add((packet, datetime.datetime.now(), False))
        self.bytes_in_net += len(packet_bytes)

        print("\nCREATED PACKET\n=======================================")
        print(packet)

        # Send packet
        self.socket.send(packet_bytes)
        print("\nSENT PACKET\n=======================================")

    def calc_packet_size(self):
        return min(self.congestion_window, self.dest_window) * self.MSS - self.bytes_in_net

    def print_state(self):
        pairs = [
            ("Window", self.congestion_window),
            ("RTT", self.RTT),
            ("Next Packet", self.next_packet),
            ("MMS", self.MSS),
            ("Bytes in Net", self.bytes_in_net)]
        string = ""
        for pair in pairs:
            string += "%s: %s\n" % pair
        print(string)
