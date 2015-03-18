__author__ = 'njhazelh'

import re


class TraceLine:
    LINE_REGEX = re.compile(
        "([\+\-rd]) (\d*\.\d*|\d*) (\d*) (\d*) (tcp|ack|cbr) (\d*) .*? (\d*) (\d)*\.\d* (\d*)\.\d* (\d*) (\d*)")

    def __init__(self, event, time, frm, to, type, size, flow, src, dest, seq, id):
        self.event = event
        self.time = float(time)
        self.frm = int(frm)
        self.to = int(to)
        self.type = type
        self.size = int(size)
        self.flow = int(flow)
        self.src = int(src)
        self.dest = int(dest)
        self.seq = int(seq)
        self.id = int(id)

    @staticmethod
    def match(line):
        return TraceLine.LINE_REGEX.match(line)

    @classmethod
    def fromLine(cls, line):
        match = TraceLine.match(line)
        if match is not None:
            return cls(match.group(1),
                       match.group(2),
                       match.group(3),
                       match.group(4),
                       match.group(5),
                       match.group(6),
                       match.group(7),
                       match.group(8),
                       match.group(9),
                       match.group(10),
                       match.group(10))
        else:
            return None


    def __str__(self):
        string = "{event} {time} {from} {to} {type} {size} {src} {dest} {seq} {id}"
        return string.format(event=self.event,
                             time=self.time,
                             frm=self.frm,
                             to=self.to,
                             type=self.type,
                             size=self.size,
                             flow=self.flow,
                             src=self.src,
                             dest=self.dest,
                             seq=self.seq,
                             id=self.id)