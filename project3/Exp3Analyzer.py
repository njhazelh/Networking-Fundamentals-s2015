__author__ = 'njhazelh'

import pandas as pd
import matplotlib as plt
import

class Exp3Analyzer:
    EXPR3_COLUMNS = ["TCP","Queue","Time","Throughput","Droprate","RTT"]

    def __init__(self):
        self.df = pd.DataFrame(columns=Exp3Analyzer.EXPR3_COLUMNS)

    def add_result(self, results):
        self.df = self.df.append(results, ignore_index=True)

    def run_analysis(self):
        self.df.to_csv("results/experiment3/experiment3.csv")
        analyze(df)


def analyze(df):
    for tcp, group in df.groupby("TCP"):
        queues = df["Queue"].unique()

        for queue in queues:
            



if __name__ == "__main__":
    df = pd.read_csv("results/experiment2/experiment2.csv", index_col=0)
    analyze(df)
