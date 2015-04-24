#!/usr/bin/python3

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from collections import Counter
import sys, argparse, urllib, urllib2, time, os

__author__ = 'msuk'

MAX_SIZE = 200

"""
Implement HTTP Server
Handles the responses for HTTP Requests
"""
class HTTPHandler():
	def __init__(self, port, origin, cache):
		print "Initialized"
		self.port = port
		self.origin = origin
		self.cache = cache

	def do_GET(self):
		print "DEBUG"
		print(self.origin)
		print(self.port)
		response = urllib.request.urlopen(self.origin)
		update_cache(self.cache, response)

		#self.protocol_version()
		self.send_response(200)
		self.send_header('Content-type','text/plain')
		self.end_header()

	def do_POST(self):
	# TODO: This can get completed after the milestone
		return

	"""
	Keep track of size of cached objects and update list
	"""
	def update_cache(self, url, response):
		if len(self.cache) == MAX_SIZE:
		# cannot add more to the cache
			for i in range(0, len(self.cache)):
				if url == self.cache(url):
					print "Cache Hit"
					self.cache.update(url)
				else:
				# Need to remove the object with the least number of times accessed
					print "Cache Miss"
					cache_list = []
					for i in self.cache.most_common():
						cache_list[i] = self.cache(i)
						url_to_del = cache_list[len(self.cache - 1)]
						del[url_to_del]	
		else:
			count = 0
			for i in range(0, len(self.cache)):
				if url == self.cache(url):
					"Cache Hit"
					# Increase the count of object accessed
					self.cache.update(url)
				else:
					print "Cache Miss"
					count = count + 1
			if count == len(self.cache):
			# url does not currently exist in the cache
				print "Cache Miss"
				self.cache = Counter(url)
		download_files(url, response)

	def download_files(self, url, response):
		current_file = os.getcwd() + url
		current_dir = os.path.dirname(current_file)
		print current_file
		print current_dir

		if os.path.isdir(current_dir):
			print "Cache hit"
		else:
			print "Cache miss"

		write_file = open(curent_file, 'w')
		write_file.write(response(read))


def run(port, origin):
	#port = args.port
	#origin = args.origin

	# Sever address comes from DNS
	server_address = ('', 8000)
	server_class = HTTPServer
	cache = Counter()
	#httpd = server_class(('', port), handler)
	print(port)
	print(origin)
	httpd = server_class(('', port), HTTPHandler(port, origin, cache))
	print "still in run"
	
	#TODO: May need to create own method to print the time?
	print time.asctime(), "Server is starting - %s:%s" % ('host', port)
	print "Serving forever"
	try:
		httpd.serve_forever()
		# Do I want this to run forever?
	except KeyboardInterrupt:
		pass
	httpd.server_close()
	print "\n", time.asctime(), "Server is stopping - %s:%s" %('host', port)

# May take out 
def run_while_true(port, origin):
	while keep_running():
		httpd.handle_request()

"""
Grab port and origin from the command line
"""
if __name__ == "__main__":
	#parser = argparse.ArgumentParser(description="A simple HTTP Server")
	#parser.add_argument('-p', dest = 'port', type = int, required = True, help = "port")
	#parser.add_argument('-o', dest = 'origin', type = str, required = True, help = "origin server name")
	#args = parser.parse_args()
	#main(args)
	port = 8080
	origin = 'ec2-52-4-98-110.compute-1.amazonaws.com'
	run(port, origin)
