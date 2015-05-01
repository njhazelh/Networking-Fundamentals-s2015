# Project 5: CDN
Nick Jones, Michelle Suk

## Overview
This project involves the creation of a Content Distribution Network (CDN).  A
content distribution network used DNS redirection to point a client to one of
many cache servers.  These cache servers generally offer far better completion
times compared to the origin server, which they mirror.  Additionally, by
directing clients to cache servers rather than the origin server, CDNs take the
load off the origin server.  Note that these cache servers are significantly
lighter than the origin.  While the origin could consist of a large data-center,
cache servers can be very light.  This one is limited to 10MB of memory/disk use.

## Components
### DNS Server
The DNS Server is pretty simple, basically it's
[Groot](https://www.youtube.com/watch?v=ph_l7Pp_1mk). For any query, it
responds as though the client was asking for the cdn domain name.  We were
able to make this simplification due to the project requirements that
the server would only be queried for the domain name given in the arguments.

The DNS server chooses from one of several ip addresses to EC2 servers, which
it looks up using their respective domain names when the server first starts.
At the moment, the selection process if completely random, since we ran out of
time while implementing the rest of the code due to final projects in other
classes.  As such, performance is rather bad.  If we had more time we would
pursue a combination of GeoIP and active monitoring.  It would be interesting
to try teaching the allocation policy to the dns server using Perceptron
classification or some other form of AI.  To do this, however, we would need
a significantly better testing system, so we could run thousands of iterations
against the servers.

The DNS Server was implemented by Nick Jones.

### HTTP Server
A simple HTTP Server was implemented using the BasicHTTPServer Python library.
The server is given a port run on and an origin server.  The http server assumes
that the origin server is running on port 8080 as stated in
/course/cs5700sp15/ec2-hosts.txt on the CCIS servers.

The basic caching functionality of our server currently uses a least
frequently used algorithm.  It stores data using the python shelve module, which
is a persistent keystore.  We decided on this, because it would allow us to manage
the files that we need easily.  We would liked to have used MongoDB or Redis, but
these would have needed installation on the server, and taken up space.  Shelve
is lightweight and standard to python.  Hopefully it is efficient enough under
the load of several thousand entries.

We keep track of data usage using a slightly imperfect method.  First, we
assume that the data used by an entry is the sum of the number of characters in
its path and body.  In python memory, there is a small overhead of about
20 Bytes for strings, and in shelve (which uses pickle) there may be meta data.
On the other hand, pickle seems to have a certain degree of compression.
Hopefully, any overhead will be insignificant compared to the data size.
We set our limit to 9MB instead of 10MB to give a solid buffer for us to work
within.  There may be better ways to do this, but since we implemented using
python, dealing directly with data size in bytes is somewhat more difficult
than with a language like C.

The HTTP Server was started by Michelle Suk and finished by Nick Jones.

### CDN
The deploy script uploads the dns server to /home/$username/dns_server on
cs5700cdnproject.ccs.neu.edu. It also uploads the http server to each
of the EC2 servers named in /course/cs5700sp15/ec2-hosts.txt on the CCIS servers.
The port number given is used for both the http and dns servers, as stated in
the project requirements.

The run script starts the dns and http servers using nohup and catches the
output in log files.  While we have log statements throughout the code, these
are currently set to a CRITICAL only level.  Our statements are DEBUG level, so
there shouldn't be any output.

The stop script stops the dns and http servers using
```killall -u $username <process name>```

The CDN deploy/run/stop scripts were implemented by Nick Jones.

## How to Run
To run the DNS Server:
```
./dnsserver -p <PORT_TO_RUN_ON> -n <DOMAIN_NAME_TO_SERVE>
```

To run the HTTP Server:
```
./httpserver -p <PORT_TO_RUN_ON> -o <ORIGIN_NAME>
```

To deploy/run/stop the full CDN:
```
./[deploy|run|stop]CDN -p <port> -o <origin> -n <name> -u <username> -i <keyfile>
```

## Testing
For the DNS server, we tested using wireshark and dig.
For the HTTP server, we tested using wget and curl.  We also output status logs
using leveled log statements.  These are disabled in the live code.

We also wrote a smallscript that encapsulates the dns search and lookup.  To run
it type ```./cdnget <domain> <port> <file>```
