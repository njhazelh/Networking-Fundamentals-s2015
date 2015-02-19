#! /usr/bin/python3

import argparse
import time
import logging

from Strategy import Strategy


logging.basicConfig(
    format='[%(asctime)s] {%(filename)-20s:%(lineno)-3d} %(levelname)s - %(message)s',
    datefmt='%I:%M:%S'
)
log = logging.getLogger("webcrawler")


def main(args):
    """
    Create and run the strategy
    :param args: Command line arguments containing args parsed by argparse
    """
    log.info("Starting webcrawler with %s %s", args.username, args.password)
    start = time.time()
    strategy = Strategy()
    strategy.run(args.username, args.password)
    end = time.time()
    diff = end - start
    minutes = int(diff / 60)
    seconds = int(diff % 60)
    log.info("Ran in {} minutes {} seconds".format(minutes, seconds))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find all the secret keys hidden on Fakebook")
    parser.add_argument("username", help="The username of the user on Fakebook to crawl on")
    parser.add_argument("password", help="The password of the user on Fakebook to crawl on")
    parser.add_argument("--verbosity", "-v", default="CRITICAL",
                        choices=["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"],
                        help="The verbosity of the output. Defaults to CRITICAL")
    args = parser.parse_args()
    log.setLevel(args.verbosity)
    main(args)
