# Networking-Fundamentals-s2015
This is a repo for Networking Fundamentals projects in Spring 2015.

## Projects:
### Assignment 1:
Does Math.  Project was designed to introduce us to network programming.

### Assignment 2:
A Webcrawler.  Project was designed to introduce us to HTTP.  The webcrawler uses
a custom implementation of HTTP on top of Pythons TCP socket.  It logs into the
fakebook website (supplied by Professor Choffnes) and follows links until it
find all the secret keys.

### Assignment 3:
A series of network simulations regarding TCP Variants.  Simulations run in
NS2, which is run as a subprocess in python.  There's a report.

### Assignment 4:
Basically wget.  We had to implement TCP and IP.  We also repurposed our
work from Project 2.

### Assignment 5:
A CDN (Content Distribution Network).  The basic concept of this project was that the professor set up a server of public wiki information located at a fixed location.  We were provided with a collection of EC2 instances located throughout the world and a DNS server located on the NEU CCIS network.  Our job was to create two programs.  The first was a web server that served cached information from the origin server.  The second was a DNS server that could be queried for a specific DNS address and would respond with the IP address of the web cache that would give the optimal responsiveness.
