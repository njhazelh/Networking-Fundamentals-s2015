#! /usr/bin/python3

import parseargs
import strategy

def main(args):
    """
    Create the neccessary objects and begin the search
    """
    strategy = Strategy()
    strategy.start()
    strategy.end()

if __name__ is "__main__":
    main()
