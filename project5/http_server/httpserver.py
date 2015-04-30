#!/usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from collections import Counter
import sys, argparse, urllib, urllib2, time, os

__author__ = 'msuk'

MAX_SIZE = 200

"""
Implement HTTP Handler
Handles the responses for HTTP Requests
The web server should communicate with the origin server over the default port.
Therefore, the port does not need to be specified.
"""
class HTTPHandler(BaseHTTPRequestHandler):
	def __init__(self, origin, cache, *args):
		print "Initialized"
		self.origin = origin
		self.cache = cache
		BaseHTTPRequestHandler.__init__(self, *args)

	"""
	Format of HTTP request for content:
		'GET /request-URI HTTP/version'

	Format of HTTP response:
		HTTP/[VERSION] [STATUS CODE] [TEXT PHRASE]
		Field1: Value1
		Field2: Value2
	"""

	"""
	Grabs files from the origin server
	"""
	def fetch_files(self, response_path):
		current_file = os.getcwd() + response_path
		current_dir = os.path.dirname(current_file)
		print current_file
		print current_dir

		if os.path.isdir(current_dir):
			print "Cache hit"
		else:
			print "Cache miss"

		write_file = open(current_file, 'w')
		write_file.write(response(read))


	"""
	Keep track of size of cached objects and update list
		If the desired file is in the cache, file is in server - increase count
		If the desired file is not in the cache, need to grab from origin server
	"""
	def update_cache(self, url, response):
		print "In update cache"
		count = 0
		if len(self.cache) == MAX_SIZE:
		# cannot add more to the cache
			for i in range(0, len(self.cache)):
				if url == self.cache(url):
					print "The path was found in the dictionary!"
					self.cache.update(url)
				else:
				# Need to remove the object with the least number of times accessed
					print "The path was not found in the dictionary!"
					cache_list = []
					for i in self.cache.most_common():
						cache_list[i] = self.cache(i)
						url_to_del = cache_list[len(self.cache - 1)]
						del[url_to_del]	
		else:
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
		self.fetch_files(response)

	def do_GET(self):
		print "In GET"
		print("Origin:", self.origin)
		print("Path?", self.path)
		default_port = '8080'
		html = ''
		response = ''
		resp = ''

		"""
		URL format: 'protocol://server/request-URI'
			protocol: how to tell server which document is being request[HTTP]
			server: which server to contact
			request-URI: name to identify document
		"""

		protocol = "http://"
		print("Protocol:", protocol)
		#request = protocol + self.origin + ":" + default_port + self.path
		request = protocol + self.path
		print("Request:", request)
		
		if os.path.exists(request):
			print "Cache hit"
		else:
			print "Cache miss"	
			try:
				response = urllib2.urlopen(request).readlines()
				print(response)
			except urllib2.URLError as err:
				print "Failed to reach server."
				print(err.reason)
			except urllib2.HTTPError as err:
				print "The server couldn't fulfill the request."
				print(err.getcode())
			else:
				html = response.read()
				resp = response.geturl()

		print "Response Read:"
		print(html)
		print "Response URL:"
		print(resp)
		self.update_cache(self.cache, response)


		#self.protocol_version()
		self.send_response(200)
		# Ordinary text is specified by 'text/plain'
		self.send_header('Content-type','text/plain')
		self.end_headers()
		self.wfile.write("This should be where the response goes")
		self.wfile.write(response)
		# The response should be what is being written

	def do_POST(self):
	# TODO: This can get completed after the milestone
		return

def run(port, origin):
	#port = args.port
	#origin = args.origin

	# Sever address comes from DNS
	server_address = ('', 8000)
	server_class = HTTPServer
	cache = Counter()
	print(port)
	print(origin)
	# Do I need to bind the server/socket to the port?  Since I am not specifying the host being used
	
	def handler(*args):
		HTTPHandler(origin, cache, *args)
	httpd = server_class(('', port), handler)
	
	print time.asctime(), "Server is starting - %s:%s" % ('host_not_specified_yet', port)
	print "Serving forever"
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()
	print "\n", time.asctime(), "Server is stopping - %s:%s" %('host_not_specified_yet', port)

"""
Grab port and origin from the command line
The port is the line of communication between the user and the web server.
"""
if __name__ == "__main__":
	#parser = argparse.ArgumentParser(description="A simple HTTP Server")
	#parser.add_argument('-p', dest = 'port', type = int, required = True, help = "port")
	#parser.add_argument('-o', dest = 'origin', type = str, required = True, help = "origin server name")
	#args = parser.parse_args()
	#run(args)

	# Put these two in here just for testing
	#port = 8080
	#origin = 'ec2-52-4-98-110.compute-1.amazonaws.com'
	port = 43434
	origin = "localhost"
	run(port, origin)