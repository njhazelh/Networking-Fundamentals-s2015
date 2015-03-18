import subprocess
import re

# p = subprocess.Popen("ns experiment2.tcl 0 1 0".split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
# for line in iter(p.stdout.readline, b''):
# line = line.decode("utf-8").trim()
#     print(line)
#
# print("DONE")
import sys

ITERATIONS = 1
CLEAR_LINE = "\033[2K"


class TraceLine:
    LINE_REGEX = re.compile(
        "([\+\-rd]) (\d*\.\d*|\d*) \d* \d* (tcp|ack|cbr) (\d*) .*? (\d*) (\d)*\.\d* (\d*)\.\d* (\d*) (\d*)")

    def __init__(self, event, time, type, size, flow, src, dest, seq, id):
        self.event = event
        self.time = float(time)
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
        if match:
            return TraceLine(match.group(1),
                             match.group(2),
                             match.group(3),
                             match.group(4),
                             match.group(5),
                             match.group(6),
                             match.group(7),
                             match.group(8),
                             match.group(9))
        else:
            return None

    def __str__(self):
        return "{event} {time} {type} {size} {src} {dest} {seq} {id}".format(event=self.event,
                                                                             time=self.time,
                                                                             type=self.type,
                                                                             size=self.size,
                                                                             flow=self.flow,
                                                                             src=self.src,
                                                                             dest=self.dest,
                                                                             seq=self.seq,
                                                                             id=self.id)


class Experiment2State():
    def __init__(self):
        self.RTTs = []
        self.send_times = dict
        self.dropped = 0
        self.sent = 0

    def add_line(self, line):
        pass

    def __str__(self):
        return ""


def run_test(combo, cbr):
    results = Experiment2State()
    cmd = "ns experiment2.tcl 0 {combo} {cbr}".format(combo=combo, cbr=cbr)
    with subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as p:
        for line in iter(lambda: str(p.stdout.readline(), encoding="utf-8").strip(), ""):
            obj = TraceLine.fromLine(line)
            if obj:
                results.add_line(obj)
        p.kill()
    return results


def progress_bar(done, max):
    percent = float(done) / max
    width = 20
    done_width = int(width * percent)
    rest_width = width - done_width
    sys.stdout.write(CLEAR_LINE)
    sys.stdout.write("\r[{:s}{:s}] {:d}% {:d}/{:d}".format("=" * done_width,
                                                           "-" * rest_width,
                                                           int(percent * 100), done, max,
                                                           done_width=done_width,
                                                           rest_width=rest_width))


def main():
    done = 0
    for combo in range(0, 4):
        for cbr in range(0, 10):
            for i in range(0, ITERATIONS):
                progress_bar(done, 4 * 10 * ITERATIONS)
                result = run_test(combo, cbr)
                print(CLEAR_LINE, result)
                done += 1
    print(CLEAR_LINE, "\rDONE")


if __name__ == "__main__":
    main()
