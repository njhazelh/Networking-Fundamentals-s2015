#! /usr/bin/python3

import argparse, time
from Strategy import Strategy

def main(args):
    """
    Create and run the strategy
    """
    start = time.time()
    strategy = Strategy()
    strategy.run(args.username, args.password)
    end = time.time()
    diff = end - start
    minutes = int(diff / 60)
    seconds = int(diff % 60)
    print("Ran in {} minutes {} seconds".format(minutes, seconds))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find all the secret keys hidden on Fakebook")
    parser.add_argument("username", help="The username of the user on Fakebook to crawl on")
    parser.add_argument("password", help="The password of the user on Fakebook to crawl on")
    args = parser.parse_args()
    main(args)
