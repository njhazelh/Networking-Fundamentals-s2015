from Exp1Analyzer import Exp1Analyzer
from tools import *
from CumulativeFlow import *

__author__ = 'njhazelh'


class Experiment1State(Experiment):
    def __init__(self):
        self.flow = CumulativeFlow()

    def add_line(self, line):
        if line.flow != 1:
            return
        if line.type == 'tcp' or line.type == 'ack':
            self.flow.add_line(line)

    def get_result(self):
        result = self.flow.get_result()
        return {
            "TCP": None,
            "CBR": None,
            "TCP Start (Sec)": result[0],
            "Time (Sec)": result[1],
            "Throughput (Mbps)": result[2],
            "Drop Rate %": result[3] * 100.0,
            "RTT (Sec)": result[4]
        }


def main():
    iterations = 10
    TCPs = ["Agent/TCP", "Agent/TCP/Reno", "Agent/TCP/Newreno", "Agent/TCP/Vegas"]
    cbr_max = 11
    done = 0
    total = iterations * len(TCPs) * cbr_max
    analyzer =  Exp1Analyzer()
    for tcp in TCPs:
        for cbr in range(0, cbr_max):
            for i in range(0, iterations):
                progress_bar(done, total)
                result = run_test(["ns", "experiment1.tcl", tcp, str(cbr)], Experiment1State)
                result["TCP"] = tcp
                result["CBR"] = cbr
                analyzer.add_result(result)
                done += 1
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
