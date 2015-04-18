#!/usr/bin/python3

#from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from collections import Counter
import sys, argparse

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
		#self.protocol_version()
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

def main(args):
	port = args.port
	origin = args.origin

"""
Grab port and origin from the command line
"""
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="A simple HTTP Server")
	parser.add_argument('-p', dest = 'port', type = int, required = True, help = "port")
	parser.add_argument('-o', dest = 'origin', type = str, required = True, help = "origin server name")
	args = parser.parse_args()
	main(args)
