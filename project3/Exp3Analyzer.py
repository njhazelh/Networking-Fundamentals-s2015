__author__ = 'njhazelh'

import pandas as pd
from tools import CLEAR_LINE

class Exp3Analyzer:
    EXPR3_COLUMNS = []

    def __init__(self):
        self.df = pd.DataFrame(columns=Exp3Analyzer.EXPR3_COLUMNS)

    def add_result(self, result):
        self.df = self.df.append([result], ignore_index=True)

    def run_analysis(self):
        print(CLEAR_LINE, "\r", self.df.to_string())
        self.df.to_csv("results/experiment3/experiment3.csv")
