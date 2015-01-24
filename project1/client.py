#!/usr/bin/python

import sys, re, argparse

__author__ = 'Nick Jones'

parser = argparse.ArgumentParser(description="Do lots of meaningless math over the network!")
parser.add_argument("-p", "--port", help="The server port to connect to", type=int, default=27993)
parser.add_argument("-s", "--secure", help="Use a secure socket", action='store_true')
parser.add_argument("hostname", help="The hostname of the server")
parser.add_argument("id", help="The NEU id of the student running the program.  Must have all leading zeros.")
args = parser.parse_args()
print(args)

def main():
    """
    This is the entry point for the program.

    To run the program, run the following in the command line.
        ./client <-p port> <-s> [hostname] [NEU ID]

    Run "./client -h" for more info

    :return: Return nothing.
    """
    # TODO: Create Socket Connection
    # TODO: Send initial message
    # TODO: DO ALL THE MESSAGE PASSING!
    # TODO: Catch the final value and exit
    pass


if __name__ == "__main__":
    main()
