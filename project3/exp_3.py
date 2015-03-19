from CumulativeFlow import CumulativeFlow
from Exp3Analyzer import Exp3Analyzer
from tools import *

__author__ = 'njhazelh'


class Experiment3State(Experiment):
    INTERVAL = 0.25

    def __init__(self):
        self.interval = Experiment3State.INTERVAL
        self.limit = Experiment3State.INTERVAL
        self.results = []
        self.flow = CumulativeFlow()


    def add_line(self, line):
        if line.time >= self.limit:
            self.save_reset_flow()
        self.flow.add_line(line)

    def save_reset_flow(self):
        time = self.limit
        result = self.flow.get_result()
        results = list(result)
        results.insert(0, time)
        self.results.append(results)
        self.limit += self.interval
        self.flow.reset()


    def get_result(self):
        self.save_reset_flow()
        results = []
        for result in self.results:
            results.append({
                "TCP": None,
                "Queue": None,
                "Time": result[0],
                "Throughput": result[3],
                "Droprate": result[4],
                "RTT": result[5]
            })
        return results

def main():
    iterations = 10
    queues = ["RED", "DropTail"]
    TCPs = ["Reno", "Sack1"]
    done = 0
    total = iterations * len(queues) * len(TCPs)
    analyzer = Exp3Analyzer()
    for queue in queues:
        for tcp in TCPs:
            for i in range(0, iterations):
                progress_bar(done, total)
                cmd = ["ns", "experiment3.tcl", queue, tcp]
                results = run_test(cmd, Experiment3State)
                for result in results:
                    result["Queue"] = queue
                    result["TCP"] = "Agent/TCP/" + tcp
                analyzer.add_result(results)
                done += 1
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
