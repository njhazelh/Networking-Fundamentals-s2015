__author__ = 'njhazelh'

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class Exp1Analyzer:
    EXPR1_COLUMNS = ["TCP", "CBR", "Time (Sec)", "Throughput (Mbps)", "Drop Rate %", "RTT (Sec)"]

    def __init__(self):
        self.df = pd.DataFrame(columns=Exp1Analyzer.EXPR1_COLUMNS)

    def add_result(self, result):
        self.df = self.df.append([result], ignore_index=True)

    def run_analysis(self):
        self.df.to_csv("results/experiment1/experiment1.csv")
        analyze(df)

def analyze(df):
    plt.figure(1)
    plt.title("Throughput vs CBR Flow")
    plt.grid(True)
    plt.ylabel("TCP Bandwidth (Mbps)")
    plt.xlabel("CBR Bandwidth (Mbps)")

    plt.figure(2)
    plt.title("Round-trip Time vs CBR Flow")
    plt.grid(True)
    plt.ylabel("TCP Packet RTT (ms)")

    plt.figure(3)
    plt.title("Drop Rate vs CBR Flow")
    plt.grid(True)
    plt.ylabel("TCP Packet Drop Rate (%)")

    for tcp in df["TCP"].unique():
        means = df[df["TCP"] == tcp].groupby("CBR").aggregate(np.mean)

        plt.figure(1)
        means["Throughput (Mbps)"].plot(label=tcp)

        plt.figure(2)
        means["RTT (Sec)"].apply(lambda x: x* 1000).plot(label=tcp)

        plt.figure(3)
        means["Drop Rate %"].plot(label=tcp)

    plt.figure(1)
    plt.legend(loc=0)
    plt.savefig("results/experiment1/throughput.png")
    plt.close(1)
    plt.figure(2)
    plt.legend(loc=0)
    plt.savefig("results/experiment1/rtt.png")
    plt.close(2)
    plt.figure(3)
    plt.legend(loc=0)
    plt.savefig("results/experiment1/droprate.png")
    plt.close(3)

if __name__ == "__main__":
    df = pd.read_csv("results/experiment1/experiment1.csv", index_col=0)
    analyze(df)
