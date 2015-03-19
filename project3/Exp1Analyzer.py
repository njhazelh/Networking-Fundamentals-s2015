__author__ = 'njhazelh'

import pandas as pd

class Exp1Analyzer:
    EXPR1_COLUMNS = ["TCP", "CBR", "Time (Sec)", "Throughput (Mbps)", "Drop Rate %", "RTT (Sec)"]

    def __init__(self):
        self.df = pd.DataFrame(columns=Exp1Analyzer.EXPR1_COLUMNS)

    def add_result(self, result):
        self.df = self.df.append([result], ignore_index=True)

    def run_analysis(self):
        self.df.to_csv("results/experiment1/experiment1.csv")

def analyze(df):
    pass

if __name__ == "__main__":
    df = pd.read_csv("results/experiment1/experiment1.csv")
    analyze(df)
