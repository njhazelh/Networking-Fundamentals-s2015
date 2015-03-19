__author__ = 'njhazelh'

import pandas as pd

class Exp3Analyzer:
    EXPR3_COLUMNS = ["TCP","Queue","Time","Throughput","Droprate","RTT"]

    def __init__(self):
        self.df = pd.DataFrame(columns=Exp3Analyzer.EXPR3_COLUMNS)

    def add_result(self, results):
        self.df = self.df.append(results, ignore_index=True)

    def run_analysis(self):
        self.df.to_csv("results/experiment3/experiment3.csv")
