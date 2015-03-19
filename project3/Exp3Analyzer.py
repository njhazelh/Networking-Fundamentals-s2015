__author__ = 'njhazelh'

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class Exp3Analyzer:
    EXPR3_COLUMNS = ["TCP","Queue","Time","Throughput","Droprate","RTT"]

    def __init__(self):
        self.df = pd.DataFrame(columns=Exp3Analyzer.EXPR3_COLUMNS, dtype=float)

    def add_result(self, results):
        self.df = self.df.append(results, ignore_index=True)

    def run_analysis(self):
        self.df.to_csv("results/experiment3/experiment3.csv")
        analyze(self.df)


def analyze(df):
    for tcp, group in df.groupby("TCP"):
        RED_tests = group[group["Queue"] == "RED"]
        DT_tests = group[group["Queue"] == "DropTail"]
        DT_means = DT_tests.groupby("Time").agg(np.mean)
        RED_means = RED_tests.groupby("Time").agg(np.mean)

        plt.figure()
        plt.title("Throughput for DropTail vs RED Queues over time using {}".format(tcp))
        plt.grid(True)
        plt.ylabel("TCP Throughput (Mbps)")
        plt.xlabel("Time (seconds)")
        DT_means["Throughput"].plot(label="DropTail")
        RED_means["Throughput"].plot(label="RED")
        plt.legend(loc=0)
        plt.savefig("results/experiment3/{}-throughput.png".format(tcp.replace("/", "_")))
        plt.close()

        plt.figure()
        plt.title("RTT for DropTail vs RED Queues over time using {}".format(tcp))
        plt.grid(True)
        plt.ylabel("TCP RTT (ms)")
        plt.xlabel("Time (seconds)")
        DT_means["RTT"].apply(lambda x: x * 1000).plot(label="DropTail")
        RED_means["RTT"].apply(lambda x: x * 1000).plot(label="RED")
        plt.legend(loc=0)
        plt.savefig("results/experiment3/{}-rtt.png".format(tcp.replace("/", "_")))
        plt.close()

        plt.figure()
        plt.title("Drop Rate for DropTail vs RED Queues over time using {}".format(tcp))
        plt.grid(True)
        plt.ylabel("TCP Drop Rate (%)")
        plt.xlabel("Time (seconds)")
        DT_means["Droprate"].plot(label="DropTail")
        RED_means["Droprate"].plot(label="RED")
        plt.legend(loc=0)
        plt.savefig("results/experiment3/{}-droprate.png".format(tcp.replace("/", "_")))
        plt.close()


if __name__ == "__main__":
    df = pd.read_csv("results/experiment3/experiment3.csv", index_col=0)
    analyze(df)
