__author__ = 'njhazelh'

import sys
import subprocess

try:
    import statistics as stat
except ImportError:
    stat = None

from TraceLine import *


CLEAR_LINE = "\033[2K"


def progress_bar(done, max):
    percent = float(done) / max
    width = 80
    done_width = int(width * percent)
    rest_width = width - done_width
    sys.stdout.write(CLEAR_LINE)
    sys.stdout.write("\r[{:s}{:s}] {:d}% {:d}/{:d}".format("=" * done_width,
                                                           "-" * rest_width,
                                                           int(percent * 100), done, max,
                                                           done_width=done_width,
                                                           rest_width=rest_width))


def run_test(cmd, stateObject):
    results = stateObject()

    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as p:
        for line in iter(lambda: str(p.stdout.readline(), encoding="utf-8").strip(), ""):
            obj = TraceLine.fromLine(line)
            if obj:
                results.add_line(obj)
        p.kill()
    return results.get_result()


class Experiment:
    def add_line(self, line):
        raise NotImplementedError("add_line not implemented")

    def get_result(self):
        raise NotImplementedError("get_result not implemented")
