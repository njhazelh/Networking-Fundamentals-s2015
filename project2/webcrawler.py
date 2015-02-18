#! /usr/bin/python3

import argparse, timeit
from Strategy import Strategy

def main(args):
    """
    Create and run the strategy
    """
    start = timeit.timeit()
    strategy = Strategy()
    strategy.run(args.username, args.password)
    end = timeit.timeit()
    seconds = int(end - start)
    minutes = int(seconds / 60)
    seconds = seconds % 60
    print("Ran in {} minutes {} seconds".format(minutes, seconds))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find all the secret keys hidden on Fakebook")
    parser.add_argument("username", help="The username of the user on Fakebook to crawl on")
    parser.add_argument("password", help="The password of the user on Fakebook to crawl on")
    args = parser.parse_args()
    main(args)
