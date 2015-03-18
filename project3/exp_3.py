__author__ = 'njhazelh'

from tools import *

class Experiment3State(Experiment):
    def __init__(self):
        pass

    def add_line(self, line):
        pass

    def get_result(self):
        pass

def analyze(results):
    return ""

def main():
    iterations = 2
    queues = ["RED", "DropTail"]
    TCPs = ["Reno", "Sack1"]
    done = 0
    total = iterations * len(queues) * len(TCPs)
    for queue in queues:
        for tcp in TCPs:
            results = []
            for i in range(0, iterations):
                progress_bar(done, total)
                cmd = ["ns", "experiment3.tcl", queue, tcp]
                result = run_test(cmd, Experiment3State)
                results.append(result)
                done += 1
            print(analyze(results))

if __name__ == "__main__":
    main()
