#! /usr/bin/python3

import logging
import sys
from urllib.parse import urlparse
import socket

from http_browser.Browser import Browser
from http_browser.HttpServerMessage import HTTP_STATUS
from tcp.Exceptions import ClosedSocketException

__author__ = "njhazelh"

logging.basicConfig(
    format='[%(asctime)s] {%(filename)-20s:%(lineno)-3d} %(levelname)s - %(message)s',
    datefmt='%I:%M:%S')
log = logging.getLogger("rawhttpget")


def main(argv):
    """
    Get the resource from the internet.
    :param argv: The commmand line arguments parsed into a handy map.
    """
    dest, path, filename = parse_input(args.url)
    browser = Browser()
    print("Getting %s from %s" % (path, dest))
    try:
        response = browser.get(path, dest=dest)
    except ConnectionRefusedError:
        print("Could not connect to server")
        sys.exit()
    except ClosedSocketException:
        print("Socket was open but closed")
        sys.exit()
    print("Saving response to %s" % (filename))
    saveResponse(response, filename)
    browser.close()


def parse_input(url):
    if not url.startswith('http'):
        url = '%s%s' % ('http://', url)
    parsed = urlparse(url)

    # validate url
    if parsed.netloc == '':
        log.critical("domain name must be provided. Received %s", parsed)
        sys.exit(0)
    try:
        socket.gethostbyname(parsed.netloc)
    except OSError:
        print("Could not find IP address for domain name")
        sys.exit(0)

    domain = parsed.netloc
    port = 80

    # calculate filename to save result as
    if parsed.path == '' or parsed.path[-1] == "/":
        filename = "index.html"
    else:
        filename = parsed.path.split("/")[-1]

    return (domain, port), url, filename


def saveResponse(response, filename):
    if response.status_code != HTTP_STATUS.OK:
        print("Failed to load resource. Status Code = %d" % (response.status_code))
    else:
        data = response.body
        file = open(filename, 'wb')
        file.write(data)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Basically wget")
    parser.add_argument("url", help="The url to get.  Will use filename from resource or index.html if it's a folder")
    parser.add_argument("--verbosity", "-v", default="CRITICAL",
                        choices=["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"],
                        help="The verbosity of the output.  Defaults to CRITICAL.")
    args = parser.parse_args()
    log.setLevel(args.verbosity)
    main(args)
