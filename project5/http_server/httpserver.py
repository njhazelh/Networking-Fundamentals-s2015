#!/usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import logging
import urllib2
from OriginGetCache import OriginGetCache

__author__ = 'msuk'

logging.basicConfig(
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%I:%M:%S'
)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

ORIGIN_CACHE = OriginGetCache()

class CDNHandler(BaseHTTPRequestHandler):
    """
    Implement HTTP Handler
    Handles the responses for HTTP Requests
    The web server should communicate with the origin server over the default port.
    Therefore, the port does not need to be specified.

    Format of HTTP request for content:
    'GET /request-URI HTTP/version'

    Format of HTTP response:
        HTTP/[VERSION] [STATUS CODE] [TEXT PHRASE]
        Field1: Value1
        Field2: Value2
    """
    def do_GET(self):
        log.debug("Asked for GET %s", self.path)

        if ORIGIN_CACHE.has(self.path):
            log.debug("%s is in the cache", self.path)
            message = ORIGIN_CACHE.get(self.path)
            response_code = 200
            headers = []
        else:
            log.debug("Fetching %s from origin(%s)", self.path, self.server.origin)
            response_code, headers, message = self.get_from_origin(self.path)
            self.cache_response(response_code, headers, message)

        self.reply(response_code, headers, message)

    def cache_response(self, response_code, headers, message):
        if response_code == 200:
            ORIGIN_CACHE.store(self.path, message)

    def get_from_origin(self, path):
        request_url = "http://%s:%d%s" % (self.server.origin, self.server.origin_port, path)

        try:
            s = urllib2.urlopen(request_url)
            origin_request = s.read()
            return 200, [], origin_request
        except urllib2.HTTPError as e:
            return e.getcode(), [], ""
        except urllib2.URLError as e:
            log.debug(e)
            return 500, [], ""

    def reply(self, response_code, headers, message):
        """
        Send a reply to the client
        :param response_code: The HTTP response code of the reply. Eg. 200 is Success.
        :param headers: A list of the headers for the message.
        :param message: The body of the response.
        """
        self.send_response(response_code)
        for key, value in headers:
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(message)

def main(port, origin):
    """
    Entry Point
    :param port: The port to run the server on
    :param origin: The domain name of the origin.
    """
    server = HTTPServer(('', port), CDNHandler)
    server.origin = origin
    server.origin_port = 8080

    log.debug("Starting server on port %d", port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    log.debug("Stopping server.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="A simple HTTP Server")
    parser.add_argument('-p', dest = 'port', type = int, required = True, help = "port")
    parser.add_argument('-o', dest = 'origin', type = str, required = True, help = "origin server name")
    args = parser.parse_args()
    main(args.port, args.origin)
