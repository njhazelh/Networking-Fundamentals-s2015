from Exp2Analyzer import Exp2Analyzer

__author__ = 'njhazelh'

from tools import *
from CumulativeFlow import *
import numpy as np

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
        if flow1 is None or flow2 is None:
            raise Exception("Missing flows")
        flow1 = flow1.get_result()
        flow2 = flow2.get_result()

        return {
            "TCP1": None,
            "TCP2": None,
            "CBR": None,
            "TCP1 Start": flow1[0],
            "TCP2 Start": flow2[0],
            "TCP1 Time": flow1[1],
            "TCP2 Time": flow2[1],
            "TCP1 Throughput": flow1[2],
            "TCP2 Throughput": flow2[2],
            "TCP1 Droprate": flow1[3],
            "TCP2 Droprate": flow2[3],
            "TCP1 RTT": flow1[4],
            "TCP2 RTT": flow2[4],
        }

def main():
    iterations = 10
    combos = [("Reno", "Reno"), ("Newreno", "Reno"), ("Vegas", "Vegas"), ("Newreno", "Vegas")]
    cbr_max = 11
    done = 0
    cbrs = np.arange(0, cbr_max, 0.5)
    total = iterations * len(combos) * len(cbrs)
    analyzer = Exp2Analyzer()
    for combo in combos:
        for cbr in cbrs:
            for i in range(0, iterations):
                progress_bar(done, total)
                result = run_test(["ns", "experiment2.tcl", combo[0], combo[1], str(cbr)], Experiment2State)
                result["TCP1"] = combo[0]
                result["TCP2"] = combo[1]
                result["CBR"] = cbr
                analyzer.add_result(result)
                done += 1
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
