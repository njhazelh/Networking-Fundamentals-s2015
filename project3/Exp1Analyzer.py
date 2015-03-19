__author__ = 'njhazelh'

import pandas as pd
from tools import CLEAR_LINE

class Exp1Analyzer:
    EXPR1_COLUMNS = ["TCP", "CBR", "Time (Sec)", "Throughput (Mbps)", "Drop Rate %", "RTT (Sec)"]

    def __init__(self):
        self.df = pd.DataFrame(columns=Exp1Analyzer.EXPR1_COLUMNS)

    def add_result(self, result):
        self.df = self.df.append([result], ignore_index=True)

    def run_analysis(self):
        print(CLEAR_LINE, "\r", self.df.to_string())
        self.df.to_csv("results/experiment1/experiment1.csv")
