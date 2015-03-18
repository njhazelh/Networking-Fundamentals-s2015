from tools import *
from CumulativeFlow import *


class Experiment1State(Experiment):
    def __init__(self):
        self.flow = CumulativeFlow()

    def add_line(self, line):
        if line.flow != 1: return
        if line.type == 'tcp' or line.type == 'ack':
            self.flow.add_line(line)

    def get_result(self):
        return self.flow.get_result()


def analyze(results):
    points = [x for x in zip(*results)]
    return {
            "throughput": {
                "mean": mean(points[0]),
                "std": stdev(points[0])
            },
            "drop_rate": {
                "mean": mean(points[1]),
                "std": stdev(points[1])
            },
            "rtt": {
                "mean": mean(points[2]),
                "std": stdev(points[2])
            }
        }


def main():
    iterations = 2
    TCPs = ["Agent/TCP", "Agent/TCP/Reno", "Agent/TCP/Newreno", "Agent/TCP/Vegas"]
    cbr_max = 11
    done = 0
    total = iterations * len(TCPs) * cbr_max
    for tcp in TCPs:
        for cbr in range(0, cbr_max):
            results = []
            for i in range(0, iterations):
                progress_bar(done, total)
                result = run_test(["ns", "experiment1.tcl", tcp, str(cbr)], Experiment1State)
                results.append(result)
                sys.stdout.write("{}\r{} {}Mbps {}: {} \n".format(CLEAR_LINE, tcp, cbr, i, str(result)))
                done += 1
            print(analyze(results))

    sys.stdout.write(CLEAR_LINE + "\rDONE\n")


if __name__ == "__main__":
    main()
