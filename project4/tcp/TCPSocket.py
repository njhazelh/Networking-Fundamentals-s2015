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
        self.src = (HOST, random.randrange(0, 1 << 16))
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
        self.segments_in_net = 0
        self.RTT = None
        self.MSS = 536
        self.next_packet = {
            'fin': False,
            'syn': False,
            'ack': False,
            'ack_num': 1,
            'seq': 1000#random.randrange(0, 1 << 32)
        }
        self.current_send_packet = None
        self.packets_in_network = set()
        self.resend_queue = queue.PriorityQueue()
        self.current_resend_packet = None
        self.data_read = 0

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
        """
        self.check_socket_error()

        if self.current_recv_packet is None:
            packet = None
            while True:
                self.check_socket_error()
                if not self.data_recv_queue.empty():
                    packet = self.data_recv_queue.get(block=False)
                    if int.from_bytes(packet[2:3], 'big') == self.src[1]:
                        break
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
        p = TCPPacket.fin(self.src, self.dest, self.next_packet['seq'])
        p.set_checksum()
        self.socket.send(p.to_bytes())

    def force_die(self):
        print("KILLING IT")
        self.next_packet['seq'] = 0
        syn = TCPPacket.syn(self.src, self.dest, self.next_packet['seq'])
        syn.set_checksum()
        self.socket.send(syn.to_bytes())
        p = None
        while True:
            p = self.socket.recv()
            if p is None:
                continue
            p = TCPPacket.from_network(p, self.dest[0], self.src[0])
            if p.src == self.dest and p.dest == self.src:
                break
            time.sleep(1.0 / 1000)
        self.next_packet['ack_num'] = p.seq + len(p.data)
        self.next_packet['seq'] = p.ack_num
        fin = TCPPacket.fin(self.src, self.dest, self.next_packet['seq'])

        fin.set_checksum()
        self.socket.send(fin.to_bytes())
        while True:
            p = self.socket.recv()
            if p is None:
                continue
            p = TCPPacket.from_network(p, self.dest[0], self.src[0])
            if p.src == self.dest and p.dest == self.src and p.fin and p.ack:
                break
            time.sleep(1.0 / 1000)
        print("KILLED IT")

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
            self.print_state()
            self.send_new_packets()
            self.reset_next_packet()

            packet = self.socket.recv()
            if packet is not None:
                self.parse_packet(packet)

            self.check_timeouts()

            # Gotta avoid busy wait
            time.sleep(5.0 / 1000)

    def handshake(self):
        #self.force_die()
        self.next_packet['seq'] = random.randrange(0, 1 << 32)
        syn = TCPPacket.syn(self.src, self.dest, self.next_packet['seq'])
        syn.set_checksum()
        sent_time = datetime.datetime.now()
        self.socket.send(syn.to_bytes())
        p = None
        while True:
            p = self.socket.recv()
            if p is None:
                continue
            p = TCPPacket.from_network(p, self.dest[0], self.src[0])
            print(p)
            if p.src == self.dest and p.dest == self.src and p.syn and p.ack:
                break
            time.sleep(1.0 / 1000)
        print("GOT SYN_ACK")
        arrive_time = datetime.datetime.now()

        # Calculate Initial RTT
        self.RTT = (arrive_time - sent_time).total_seconds() * 1000

        # Get Advertised Window Info
        self.dest_window = p.window

        # Pull out MSS Information
        for o in p.options:
            if o['kind'] == 2 and o['length'] == 4:
                self.MSS = o['value']
                break

        self.next_packet['ack_num'] = p.seq + len(p.data) + 1
        self.next_packet['seq'] = p.ack_num
        ack = TCPPacket.ack(self.src, self.dest, self.next_packet['seq'], self.next_packet['ack_num'])
        ack.set_checksum()
        self.socket.send(ack.to_bytes())
        self.state = CONNECTION_STATE.OPEN
        self.next_packet['ack'] = True

    def check_socket_error(self):
        if self.state == CONNECTION_STATE.RST:
            raise ClosedSocketException()

    def reset_next_packet(self):
        self.next_packet['syn'] = False

    def parse_packet(self, packet):
        packet = TCPPacket.from_network(packet, self.dest[0], self.src[0])

        # Check validity
        check = packet.checksum()
        if check != 0:
            return

        # Packet is not part of this connection
        if packet.src != self.dest and packet.dest != self.src:
            return

        # Pull out MSS Information
        for o in packet.options:
            if o['kind'] == 2 and o['length'] == 4:
                self.MSS = o['value']
                break


        if packet.ack:
            self.handle_ack(packet)

        if packet.fin:
            self.shutdown()
            self.state = CONNECTION_STATE.CLOSED
        elif packet.rst:
            self.shutdown()
            self.state = CONNECTION_STATE.RST

        if len(packet.data) > 0:
            self.next_packet['ack'] = True

        if self.next_packet['ack_num'] == packet.seq:
            print("SEQUENCE NUMBER", packet.seq)
            self.next_packet['ack_num'] = packet.seq + len(packet.data)

        if len(packet.data) != 0 and packet.seq > self.next_packet['seq']:
            self.data_recv_queue.put(packet.data)
            self.data_read += len(packet.data)

        print(packet)
        print(self.next_packet)
        p = TCPPacket.ack(self.src, self.dest, self.next_packet['seq'], self.next_packet['ack_num'])
        p.set_checksum()
        self.socket.send(p.to_bytes())
        print("JUST ACKED", self.next_packet['ack_num'])

        self.dest_window = packet.window

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
        if packet.ack_num > self.next_packet['seq']:
            self.next_packet['seq'] = packet.ack_num

        # Find packets that were just acked.
        acked_packets = set()
        print("ACKING PACKETS WITH seq <", self.next_packet['seq'])

        for p in self.packets_in_network:
            print(p[0])
            if p[0].seq <= self.next_packet['seq']:
                acked_packets.add(p)

        if len(acked_packets) > 0:
            print("ACKED PACKETS")
            for p in acked_packets:
                print(p)
            print("\n\n\n")
        # Remove them from the packets in the network
        self.packets_in_network.difference_update(acked_packets)

        # Manage their RTTs.
        now = datetime.datetime.now()
        for p in acked_packets:
            if not p[2]:
                print("ACKING PACKET")
                # Packet didn't time out so it's valid for RTT calculation
                packet_rtt = now - p[1]
                if self.RTT is None:
                    self.RTT = packet_rtt.total_seconds() * 1000
                else:
                    self.RTT = TIME_ALPHA * self.RTT + \
                               (1 - TIME_ALPHA) * packet_rtt.total_seconds() * 1000


    def check_timeouts(self):
        if self.RTT is None:
            return

        print("CHECKING TIMEOUTS\n==========================")
        timeout_packets = []
        now = datetime.datetime.now()
        for p in self.packets_in_network:
            dt = (now - p[1]).total_seconds() * 1000
            if dt > 2 * self.RTT:
                timeout_packets.append(p)

        if len(timeout_packets) > 0:
            print("\n\n\nTIMEOUTS:\n", timeout_packets)
            self.ss_thresh = self.congestion_window / 2
            self.congestion_window = 1

            for p in timeout_packets:
                self.packets_in_network.remove(p)
                self.resend_queue.put((p[0].seq, p[0]))

    def send_new_packets(self):
        while (self.current_resend_packet is not None or
                   not self.resend_queue.empty())\
                and self.network_space() != 0:
            self.resend_packet()

        while not self.data_send_queue.empty() and self.network_space() != 0:
            self.send_new_packet()

    def resend_packet(self):
        if self.current_resend_packet is not None:
            seq, packet = self.current_resend_packet
        elif not self.resend_queue.empty():
            seq, packet = self.resend_queue.get()
        else:
            return

        max_packet_size = self.MSS

        if len(packet) <= max_packet_size:
            print("RE-SENT PACKET\n==============================", packet)
            self.socket.send(packet.to_bytes())
            self.packets_in_network.add((packet, datetime.datetime.now(), True))
            self.current_resend_packet = None
        else:
            self.current_resend_packet = packet


    def send_new_packet(self):
        max_packet_size = self.MSS

        if max_packet_size < 28:
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
            packet_data = b''
            while not self.data_send_queue.empty() and len(packet_data) < packet_size:
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
            return

        packet.set_checksum()
        packet_bytes = packet.to_bytes()

        # Track that we're sending this packet.
        self.packets_in_network.add((packet, datetime.datetime.now(), False))

        print("\nCREATED PACKET\n=======================================")
        print(packet)

        # Send packet
        self.socket.send(packet_bytes)
        print("SENT PACKET\n\n")


    def network_space(self):
        return min(self.congestion_window, self.dest_window)  - len(self.packets_in_network)

    def print_state(self):
        pairs = [
            ("Window", self.congestion_window),
            ("Dest Window", self.dest_window),
            ("SRC", self.src),
            ("DEST", self.dest),
            ("RTT", self.RTT),
            ("SS_THRES", self.ss_thresh),
            ("Next Packet", self.next_packet),
            ("MMS", self.MSS),
            ("Segs in Net", self.segments_in_net),
            ("Data Read", self.data_read)]
        string = ""
        for pair in pairs:
            string += "%s: %s\n" % pair
        print(string)
