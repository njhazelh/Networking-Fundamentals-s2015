__author__ = 'njhazelh'

import pandas as pd

from tools import CLEAR_LINE


class Exp2Analyzer:
    EXPR2_COLUMNS = ["TCP1", "TCP2", "CBR", "TCP1 Start", "TCP2 Start", "TCP1 Time", "TCP2 Time", "TCP1 Throughput",
                     "TCP2 Throughput", "TCP1 Droprate", "TCP2 Droprate", "TCP1 RTT", "TCP2 RTT"]

    def __init__(self):
        self.df = pd.DataFrame(columns=Exp2Analyzer.EXPR2_COLUMNS)

    def add_result(self, result):
        self.df = self.df.append([result], ignore_index=True)

    def run_analysis(self):
        print(CLEAR_LINE, "\r", self.df.to_string())
        self.df.to_csv("results/experiment2/experiment2.csv")
