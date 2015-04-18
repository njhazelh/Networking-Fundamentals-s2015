# httpserver

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import sys, getopt

__author__ = 'msuk'

# random number - fix
MAX_SIZE = 200

"""
	Implement HTTP Server
	Handles the responses for HTTP Requests
"""
class HTTPHandler(BaseHTTPRequestHandler):
	def __init__(self, port, origin):
		self.port = port
		self.origin = origin
		return

	def do_GET(self):
		#TODO: set the real values
		self.protocol_version('')
		self.send_response('')
		self.send_header('')
		self.end_header('')
		return

	def do_POST(self):
	# TODO: This can get completed after the milestone
		return

	def handle(self):
		return

	def send_response(self):
		return

	def send_error(self):
		return

# TODO: Add in status codes for responses Sand requests
#		Accept connections
#		HTTP header
#		Include validation tags for when caching

"""
	Implement a Least Recently Used caching algorithm
	*Could be expensive
"""

def LRU_cache(self, size):
	cache = []
	# max size
	self.size = MAX_SIZE
	self.age = ''
	return

"""
	Keep track of age of cached objects
	Each time an object is accessed, age of objects updated
"""
def cache_control(self, exp_age):
	for i in range(0,len(cache)-1):
		if self.age > exp_age:
			remove_cache()
			return
	return


def update_cache(self):
	return

"""
	If cache reaches max size, least recently used object is removed
"""
def remove_cache():
	return

"""
	Grab port and origin from the command line
"""
# TODO: Make get_port and get_origin one function
def get_port(user_input):
	opts, args = getopt.getopt(user_input[1:], "p:o")
	# Check if the user inputted two args
	if len(user_input) < 5 or len(user_input) > 5:
		# Command line either has too many args or not enough
		# Exit, not return
		return

	for i, arg in opts:
		if i == '-p':
			port = arg

	return port

def get_origin(user_input):
	opts, args = getopt.getopt(user_input[1:], "p:o")
	if len(user_input) < 5 or len(user_input) > 5:
		# Exit, not return
		return

	for i, arg in opts:
		if i == '-o':
			origin = arg

	return origin

def main():
	port = get_port(sys.argv)
	origin = get_origin(sys.argv)
	return

if __name__ == "__main__":
    main()
