#!/usr/bin/python

import socket
import logging

from DNSServer import DNSServer

logging.basicConfig(
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%I:%M:%S'
)
log = logging.getLogger()
log.setLevel(logging.CRITICAL)

__author__ = "njhazelh"

HTTP_SERVERS = [
    "ec2-52-4-98-110.compute-1.amazonaws.com",
    "ec2-52-0-73-113.compute-1.amazonaws.com",
    "ec2-52-16-219-28.eu-west-1.compute.amazonaws.com",
    "ec2-52-11-8-29.us-west-2.compute.amazonaws.com",
    "ec2-52-8-12-101.us-west-1.compute.amazonaws.com",
    "ec2-52-28-48-84.eu-central-1.compute.amazonaws.com",
    "ec2-52-68-12-77.ap-northeast-1.compute.amazonaws.com",
    "ec2-52-74-143-5.ap-southeast-1.compute.amazonaws.com",
    "ec2-52-64-63-125.ap-southeast-2.compute.amazonaws.com",
    "ec2-54-94-214-108.sa-east-1.compute.amazonaws.com"
]

def main(args):
    """
    The Entry Point
    :param args: The parsed command line arguments.
    """
    caches = [socket.gethostbyname(name) for name in HTTP_SERVERS]
    server = DNSServer(args.domain, args.port, caches)

    log.debug("DNS Server started on port %d", args.port)
    try:
        server.loop()
    except KeyboardInterrupt as e:
        pass
    log.debug("DNS Server stopped")


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
