__author__ = 'njhazelh'


class CumulativeFlow:
    def __init__(self):
        self.sent_at = dict()
        self.num_sent = 0
        self.num_dropped = 0
        self.was_dropped = dict()
        self.data_received = 0
        self.start_time = None
        self.time = 0
        self.RTTs = []

    def add_line(self, line):
        self.time = line.time

        if self.start_time is None:
            self.start_time = line.time

        if line.type == 'tcp':
            self.parse_tcp(line)
        elif line.type == 'ack':
            self.parse_ack(line)

    def parse_tcp(self, line):
        if line.event == "-":
            if line.frm == line.src:
                # new packet created
                self.sent_at[line.seq] = line.time
                self.num_sent += 1
        elif line.event == "+":
            pass
        elif line.event == 'd':
            self.num_dropped += 1
            if self.sent_at.get(line.seq, None) is not None:
                del self.sent_at[line.seq]
            self.was_dropped[line.seq] = True
        elif line.event == "r":
            if line.dest == line.to:
                self.data_received += line.size
        else:
            raise Exception("Unknown event type: {}".format(str(line)))

    def parse_ack(self, line):
        if line.event == "r" and line.dest == line.to:
            to_remove = set()
            for packet in self.sent_at:
                if packet < line.seq and not self.was_dropped.get(packet, False):
                    rtt = line.time - self.sent_at[packet]
                    self.RTTs.append(rtt)
                    to_remove.add(packet)
            for packet in to_remove:
                if self.sent_at.get(packet, None) is not None:
                    del self.sent_at[packet]
                if self.was_dropped.get(packet, None) is not None:
                    del self.was_dropped[packet]

    @property
    def drop_rate(self):
        if self.num_sent > 0:
            return float(self.num_dropped) / float(self.num_sent)
        else:
            raise Exception("No packets sent")

    @property
    def avg_rtt(self):
        if len(self.RTTs) > 0:
            return sum(self.RTTs) / len(self.RTTs)
        else:
            return 0  # raise "No packets have completed a round trip"

    @property
    def throughput(self):
        if self.start_time is None:
            raise Exception("Flow has not started yet")
        else:
            return 0.000008 * self.data_received / (self.time - self.start_time)

    def get_result(self):
        return (self.throughput, self.drop_rate, self.avg_rtt)
