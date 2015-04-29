default:
	echo "Python doesn't need compiling"

clean:
	rm -rf ./**/__pycache__
	rm -f ./**/*.pyc

test:
	python3 -m unittest discover

dist: clean clean_dist
	mkdir -p dns_dist
	cp -r dnsserver dns dns_dist/.
	mkdir -p http_dist
	cp -r httpserver http_server http_dist/.

clean_dist:
	rm -rf dns_dist
	rm -rf http_dist
