#!/usr/bin/python3

from DNSServer import DNSServer


__author__ = "njhazelh"


def main(args):
    """
    The Entry Point
    :param args: The parsed command line arguments.
    """
    server = DNSServer(args.domain, args.port)
    server.loop()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="A DNS Server for controlling CDN domain name resolution")
    parser.add_argument("-p",
                        dest="port",
                        type=int,
                        required=True,
                        help="The port to run this server on. Must be high: 40000-65535")
    parser.add_argument("-n",
                        dest="domain",
                        type=str,
                        required=True,
                        help="The name of the server that people will request")
    args = parser.parse_args()
    main(args)
