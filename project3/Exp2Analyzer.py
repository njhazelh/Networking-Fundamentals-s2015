__author__ = 'njhazelh'

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class Exp2Analyzer:
    EXPR2_COLUMNS = ["TCP1", "TCP2", "CBR", "TCP1 Start", "TCP2 Start", "TCP1 Time", "TCP2 Time", "TCP1 Throughput",
                     "TCP2 Throughput", "TCP1 Droprate", "TCP2 Droprate", "TCP1 RTT", "TCP2 RTT"]

    def __init__(self):
        self.df = pd.DataFrame(columns=Exp2Analyzer.EXPR2_COLUMNS, dtype=float)

    def add_result(self, result):
        self.df = self.df.append([result], ignore_index=True)

    def run_analysis(self):
        self.df.to_csv("results/experiment2/experiment2.csv")
        analyze(self.df)

def analyze(df):
    for name, group in df.groupby(["TCP1", "TCP2"]):
        tcp1 = name[0]
        tcp2 = name[1]
        means = df[(df["TCP1"] == tcp1) & (df["TCP2"] == tcp2)].groupby("CBR").aggregate(np.mean)
        plt.figure(1)
        plt.title("Throughput vs CBR Flow w/ {tcp1} and {tcp2}".format(tcp1=tcp1,tcp2=tcp2))
        plt.grid(True)
        plt.ylabel("TCP Bandwidth (Mbps)")
        plt.xlabel("CBR Bandwidth (Mbps)")
        means["TCP1 Throughput"].plot(label=tcp1)
        means["TCP2 Throughput"].plot(label=tcp2)
        plt.legend(loc=0)
        plt.savefig("results/experiment2/{tcp1}-{tcp2}_throughput.png".format(tcp1=tcp1, tcp2=tcp2))
        plt.close(1)

        plt.figure(2)
        plt.title("RTT vs CBR Flow w/ {tcp1} and {tcp2}".format(tcp1=tcp1, tcp2=tcp2))
        plt.grid(True)
        plt.ylabel("TCP RTT (ms)")
        plt.xlabel("CBR Bandwidth (Mbps)")
        means["TCP1 RTT"].apply(lambda x: x * 1000).plot(label=tcp1)
        means["TCP2 RTT"].apply(lambda x: x * 1000).plot(label=tcp2)
        plt.legend(loc=0)
        plt.savefig("results/experiment2/{tcp1}-{tcp2}_rtt.png".format(tcp1=tcp1, tcp2=tcp2))
        plt.close(2)

        plt.figure(3)
        plt.title("Drop Rate vs CBR Flow w/ {tcp1} and {tcp2}".format(tcp1=tcp1, tcp2=tcp2))
        plt.grid(True)
        plt.ylabel("TCP Drop Rate %")
        plt.xlabel("CBR Bandwidth (Mbps)")
        means["TCP1 Droprate"].plot(label=tcp1)
        means["TCP2 Droprate"].plot(label=tcp2)
        plt.legend(loc=0)
        plt.savefig("results/experiment2/{tcp1}-{tcp2}_droprate.png".format(tcp1=tcp1, tcp2=tcp2))
        plt.close(3)


if __name__ == "__main__":
    df = pd.read_csv("results/experiment2/experiment2.csv", index_col=0)
    analyze(df)
