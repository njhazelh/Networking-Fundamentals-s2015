#!/usr/bin/python3

# httpserver
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from collections import Counter
import sys, argparse, getopt

__author__ = 'msuk'

MAX_SIZE = 200

"""
Implement HTTP Server
Handles the responses for HTTP Requests
"""
class HTTPHandler:
	def __init__(self, port, origin):
		self.port = port
		self.origin = origin

	def do_GET(self):
		#seself.protocol_version()
		self.send_response(200)
		self.send_header('Content-type','text/plain')
		self.end_header() 

	def do_POST(self):
	# TODO: This can get completed after the milestone
		return

"""
Implement a Least Frequently Used caching algorithm
"""
class LFU_cache:
	def __init__(self):
		self.cache = Counter()

	"""
	Keep track of size of cached objects and update list
	"""
	def update_cache(self, url):
		if len(self.cache) == MAX_SIZE:
		# cannot add more to the cache
			for i in range(0, len(self.cache)):
				if url == self.cache(url):
					self.cache.update(url)
				else:
				# Need to remove the object with the least number of times accessed
					cache_list = []
					for i in self.cache.most_common():
						cache_list[i] = self.cache(i)
					url_to_del = cache_list[len(self.cache - 1)]
					del[url_to_del]	
		else:
			count = 0
			for i in range(0, len(self.cache)):
				if url == self.cache(url):
					# Increase the count of object accessed
					self.cache.update(url)
				else:
					count = count + 1
			if count == len(self.cache):
			# url does not currently exist in the cache
				self.cache = Counter(url)

"""
Grab port and origin from the command line
"""
# TODO: Make get_port and get_origin one function
def get_port(user_input):
	opts, args = getopt.getopt(user_input[1:], "p:o")
	# Check if the user inputted two args
	if len(user_input) < 5 or len(user_input) > 5:
		print 'usage: ./httpserver -p PORT -o ORIGIN'
		# Command line either has too many args or not enough
		# Exit, not return
		return

	for i, arg in opts:
		if i == '-p':
			port = arg
			#print port
	return port

def get_origin(user_input):
	opts, args = getopt.getopt(user_input[1:], "p:o")
	if len(user_input) < 5 or len(user_input) > 5:
		# Print statements are for some testing
		print len(user_input)
		print user_input
		print 'usage: ./httpserver -p PORT -o ORIGIN'
		return

	for i, arg in opts:
		if i == '-o':
			origin = arg
			#print origin
	return origin

def main():
	port = get_port(sys.argv)
	origin = get_origin(sys.argv)

if __name__ == "__main__":
    main()
