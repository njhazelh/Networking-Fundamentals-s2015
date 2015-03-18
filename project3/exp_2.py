__author__ = 'njhazelh'

from tools import *
from CumulativeFlow import *

class Experiment2State(Experiment):
    def __init__(self):
        self.flows = dict()
        self.flows.setdefault(None)

    def add_line(self, line):
        if line.flow not in {1, 2}: return
        if line.type == 'tcp' or line.type == 'ack':
            flow = self.flows.get(line.flow)
            if flow:
                flow.add_line(line)
            else:
                flow = CumulativeFlow()
                self.flows[line.flow] = flow
                flow.add_line(line)

    def get_result(self):
        flow1 = self.flows.get(1, None)
        flow2 = self.flows.get(2, None)
        if flow1 and flow2:
            return (flow1.get_result(), flow2.get_result())
        else:
            raise Exception("Missing flows")


def analyze(results):
    flows = [x for x in zip(*results)]
    points_1 = [x for x in zip(*flows[0])]
    points_2 = [x for x in zip(*flows[1])]
    return {
        1: {
            "throughput": {
                "mean": mean(points_1[0]),
                "std": stdev(points_1[0])
            },
            "drop_rate": {
                "mean": mean(points_1[1]),
                "std": stdev(points_1[1])
            },
            "rtt": {
                "mean": mean(points_1[2]),
                "std": stdev(points_1[2])
            }
        },
        2: {
            "throughput": {
                "mean": mean(points_2[0]),
                "std": stdev(points_2[0])
            },
            "drop_rate": {
                "mean": mean(points_2[1]),
                "std": stdev(points_2[1])
            },
            "rtt": {
                "mean": mean(points_2[2]),
                "std": stdev(points_2[2])
            }
        }
    }


def main():
    iterations = 2
    combos = [("Reno", "Reno"), ("Newreno", "Reno"), ("Vegas", "Vegas"), ("Newreno", "Vegas")]
    cbr_max = 11
    done = 0
    total = iterations * len(combos) * cbr_max
    for combo in combos:
        for cbr in range(0, cbr_max):
            results = []
            for i in range(0, iterations):
                progress_bar(done, total)
                result = run_test(["ns", "experiment2.tcl", combo[0], combo[1], str(cbr)], Experiment2State)
                results.append(result)
                sys.stdout.write("{}\r{} {}Mbps {}: {} \n".format(CLEAR_LINE, combo, cbr, i, str(result)))
                done += 1
            print(analyze(results))

    sys.stdout.write(CLEAR_LINE + "\rDONE\n")


if __name__ == "__main__":
    main()
