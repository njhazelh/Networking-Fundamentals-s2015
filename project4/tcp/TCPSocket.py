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
    RST_RECVD = 6
    FIN_RECVD = 7


class TCPSocket:
    """
    This class is an implementation of TCP built on a custom
    implementation of IP.  It functions as any old socket would.

        socket.send(data)
        data = socket.recv(max_bytes)

    It has been known to rival wget for speed, although it's
    nowhere near as stable.
    """
    def __init__(self):
        self.socket = None
        self.data_send_queue = queue.Queue()
        self.data_recv_queue = queue.Queue()
        self.src = (HOST, random.randrange(0, 1 << 16))
        self.state = CONNECTION_STATE.NEW
        self.thread = None

    def connect(self, dest):
        """
        Create a new connection
        :param dest: The destination (address, port)
        """
        if self.thread is not None and self.thread.is_alive():
            # Already connected
            return

        # Connection State
        self.socket = IPSocket(HOST)
        self.socket.connect(dest)
        self.dest = (socket.gethostbyname(dest[0]), dest[1])

        # I/O
        self.current_recv_packet = None

        # TCP Algorithm Fields

        # The slow start threshold.
        self.ss_thresh = float("inf")

        # This is the congestion window here.
        self.congestion_window = 1

        # This is the advertised window at the destination.
        self.dest_window = float('inf')

        # Round Trip Time in ms
        self.RTT = None

        # The Max Segment Size.  The default is 536 = 576 - IP_HEADER - TCP_HEADER
        self.MSS = 536

        # This contains information regarding how the next packet should look.
        self.next_packet = {
            'fin': False,
            'syn': False,
            'ack': False,
            'ack_num': 1,
            'seq': random.randrange(0, 1 << 32)
        }

        # This is the remainder of the data for a packet that we already sent part of.
        self.current_send_packet = None

        # This is the collection of packets that are currently in the network.
        self.packets_in_network = set()

        # This is a queue of packets which must be resent, sorted into seq number order
        self.resend_queue = queue.PriorityQueue()

        # This is the seq number that needs to be acked to move the window.
        # All previous sequence numbers have been acked.
        # Following sequence numbers may have been acked, but we don't know until we
        # receive this sequence number
        self.frontier_seq = 0

        # This is a queue of all sequences that have been sent and will be acked.
        self.seq_frontiers = queue.PriorityQueue()

        # The number of bytes of data read so far.
        self.data_read = 0

        self.out_of_order_packets = queue.PriorityQueue()
        self.seen_seq_nums = set()

        # start the thread
        self.thread = threading.Thread(name="tcp-loop", target=self.loop)
        self.thread.setDaemon(True)
        self.thread.start()

    def send(self, data):
        """
        Send some data over the network. The same as sendall.
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
        :return: A byte string obtained via the socket with fewer than max_bytes bytes.
        """
        packet = b''
        self.check_socket_error()

        if self.current_recv_packet is None:
            while True:
                self.check_socket_error()
                if not self.data_recv_queue.empty():
                    packet += self.data_recv_queue.get(block=False)
                    time.sleep(0)
                else:
                    break
            if max_bytes is not None and len(packet) > max_bytes:
                self.current_recv_packet = packet[max_bytes:]
                packet = packet[:max_bytes]
        else:
            packet = self.current_recv_packet
            if max_bytes is None or len(packet) <= max_bytes:
                self.current_recv_packet = None
            else:
                self.current_recv_packet = packet[max_bytes:]
                packet = packet[:max_bytes]

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
        p = TCPPacket.fin(self.src, self.dest, self.frontier_seq)
        p.set_checksum()
        self.socket.send(p.to_bytes())

    # ================================================================
    #
    # HELPER METHODS
    #
    # ================================================================

    def loop(self):
        """
        Thread target for running TCP separate from application.
        """
        self.handshake()

        while self.state != CONNECTION_STATE.CLOSED:
            self.send_new_packets()

            while True:
                packet = self.socket.recv()
                if packet is not None:
                    self.parse_packet(packet)
                else:
                    break

            if self.state == CONNECTION_STATE.RST_RECVD or self.state == CONNECTION_STATE.FIN_RECVD:
                self.shutdown()
                break

            self.check_timeouts()

            # Gotta avoid busy wait
            time.sleep(50.0 / 1000)

    def handshake(self):
        """
        Perform the three-way handshake.
        """

        # Choose the starting seq number
        self.frontier_seq = random.randrange(0, 1 << 32)

        # Send the SYN packet to create the connection
        syn = TCPPacket.syn(self.src, self.dest, self.frontier_seq)
        syn.set_checksum()
        sent_time = datetime.datetime.now()
        self.socket.send(syn.to_bytes())

        # Get packets until we see a SYN_ACK from the destination to us.
        p = None
        while True:
            p = self.socket.recv()
            if p is None:
                continue
            p = TCPPacket.from_network(p, self.dest[0], self.src[0])
            if p.src == self.dest and p.dest == self.src and p.syn and p.ack:
                break
            time.sleep(10.0 / 1000)

        # Calculate Initial RTT
        arrive_time = datetime.datetime.now()
        self.RTT = (arrive_time - sent_time).total_seconds() * 1000

        # Get Advertised Window Info
        self.dest_window = p.window

        # Pull out MSS Information
        for o in p.options:
            if o['kind'] == 2 and o['length'] == 4:
                self.MSS = o['value']
                break

        # Calculate next seq numbers to see.
        self.next_packet['next_expected_seq'] = p.seq + len(p.data) + 1
        self.frontier_seq = p.ack_num

        # Send the ACK packet to open the connection of both sides.
        ack = TCPPacket.ack(self.src, self.dest, self.frontier_seq, self.next_packet['next_expected_seq'])
        ack.set_checksum()
        self.socket.send(ack.to_bytes())

        self.state = CONNECTION_STATE.OPEN

    def check_socket_error(self):
        """
        If there's a socket, error raise an exception.
        """
        if self.state == CONNECTION_STATE.RST:
            raise ClosedSocketException()


    def parse_packet(self, packet):
        """
        Convert the packet to an object.
        Filter packets that aren't part of this connection.
        Store data and ACK appropriately.
        :param packet: A byte string containing a tcp packet.
        """
        packet = TCPPacket.from_network(packet, self.dest[0], self.src[0])

        # Check validity
        if not packet.is_valid(self.dest, self.src):
            return

        # Pull out MSS Information
        for o in packet.options:
            if o['kind'] == 2 and o['length'] == 4:
                self.MSS = o['value']
                break

        # Handle ACK
        if packet.ack and packet.ack_num >= self.frontier_seq:
            self.handle_ack(packet)

        # ACK this packet if it contains data or FIN or SYN
        self.next_packet['ack'] = (len(packet.data) > 0) or packet.syn

        # Update the next expected seq number
        next_seq = packet.seq + len(packet.data)
        if len(packet.data) > 0 and packet.seq == self.next_packet['next_expected_seq']:
            # This is the packet we need.
            self.next_packet['next_expected_seq'] = next_seq
            self.data_recv_queue.put(packet.data)
            self.data_read += len(packet.data)
            while not self.out_of_order_packets.empty():
                p = self.out_of_order_packets.get()
                if p.seq == next_seq:
                    self.data_recv_queue.put(p.data)
                    self.data_read += len(p.data)
                    next_seq = p.seq + len(p.data)
                else:
                    self.out_of_order_packets.put(p)
                    break
        elif len(packet.data) > 0 and packet.seq > self.next_packet[
            'next_expected_seq'] and packet.seq not in self.seen_seq_nums:
            # Packet is too early, store it.
            self.out_of_order_packets.put(packet)
            self.seen_seq_nums.add(packet.seq)

        # Ack the packet if it has data
        if self.next_packet['ack']:
            p = TCPPacket.ack(self.src, self.dest, self.frontier_seq, self.next_packet['next_expected_seq'])
            p.set_checksum()
            self.socket.send(p.to_bytes())

        self.dest_window = packet.window

        if packet.fin:
            self.state = CONNECTION_STATE.FIN_RECVD
        elif packet.rst:
            self.state = CONNECTION_STATE.RST_RECVD

    def handle_ack(self, packet):
        """
        Handles the ACK clocking part of TCP.
        """
        # Increase the congestion window.
        if self.congestion_window < self.ss_thresh:
            self.congestion_window += 1
        else:
            self.congestion_window += 1 / self.congestion_window

        # Increase sequence number to next byte the destination wants.
        self.frontier_seq = packet.ack_num  # self.seq_frontiers.pop()

        # Find packets that were just acked.
        acked_packets = set()

        for p in self.packets_in_network:
            if p[0].seq <= self.next_packet['seq']:
                acked_packets.add(p)

        # Remove them from the packets in the network
        self.packets_in_network.difference_update(acked_packets)

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


    def check_timeouts(self):
        """
        Check to see if any previously sent packets have timed out while waiting to be
        ACKed
        """
        if self.RTT is None:
            return

        timeout_packets = []
        now = datetime.datetime.now()
        for p in self.packets_in_network:
            dt = (now - p[1]).total_seconds() * 1000
            if dt > 2 * self.RTT:
                timeout_packets.append(p)

        if len(timeout_packets) > 0:
            self.ss_thresh = self.congestion_window / 2
            self.congestion_window = 1

            for p in timeout_packets:
                self.packets_in_network.remove(p)
                self.resend_queue.put((p[0].seq, p[0]))

    def send_new_packets(self):
        """
        Send new packets containing the data passed into the socket via send,
        and resend timed out packets. Do so until the window if full.
        """
        while not self.resend_queue.empty() and self.network_space() > 0:
            self.resend_packet()

        while not self.data_send_queue.empty() and self.network_space() > 0:
            self.send_new_packet()

    def resend_packet(self):
        """
        If there are any packets that have timed out, send the one with the lowest
        sequence number
        """
        if not self.resend_queue.empty():
            seq, packet = self.resend_queue.get()
        else:
            return

        max_packet_size = self.MSS

        if len(packet) <= max_packet_size:
            self.socket.send(packet.to_bytes())
            self.packets_in_network.add((packet, datetime.datetime.now(), True))
            self.current_resend_packet = None
        else:
            self.current_resend_packet = packet


    def send_new_packet(self):
        """
        If there is any data to send, send a packet containing it.
        """
        max_packet_size = self.MSS

        # Get data
        if self.state == CONNECTION_STATE.OPEN:
            # Send a packet of data or ack another packet.
            packet_data = b''
            while not self.data_send_queue.empty() and len(packet_data) < max_packet_size:
                packet_data += self.data_send_queue.get()

            # Create packet
            packet = TCPPacket(self.src,
                               self.dest,
                               self.frontier_seq,
                               self.next_packet['next_expected_seq'],
                               packet_data)
        else:
            return

        packet.ack = True

        packet.set_checksum()
        packet_bytes = packet.to_bytes()

        # Track that we're sending this packet.
        self.packets_in_network.add((packet, datetime.datetime.now(), False))


        # Send packet
        self.socket.send(packet_bytes)


    def network_space(self):
        """
        How many more MSS can you fit into the WINDOW.
        :return: The number of segments remaining to fit.
        """
        return min(self.congestion_window, self.dest_window) / self.MSS - len(self.packets_in_network)
