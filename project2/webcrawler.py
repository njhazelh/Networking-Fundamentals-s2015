#! /usr/bin/python3

import argparse
import Strategy

def main(args):
    """
    Create and run the strategy
    """
    strategy = Strategy()
    strategy.run(args.username, args.password)

if __name__ is "__main__":
    parser = argparse.ArgumentParser(description="Find all the secret keys hidden on Fakebook")
    parser.add_argument("username", help="The username of the user on Fakebook to crawl on")
    parser.add_argument("password", help="The password of the user on Fakebook to crawl on")
    args = parser.parse_args()
    main(args)
