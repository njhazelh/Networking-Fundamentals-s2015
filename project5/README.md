# Project 5: CDN
Nick Jones, Michelle Suk

## Overview
This project involves the creation of a Content Distribution Network (CDN).

## Components
### DNS Server
The DNS Server is pretty simple, basically [Groot](https://www.youtube.com/watch?v=ph_l7Pp_1mk).
For any query, it responds with the same response.  We were able to make this
simplification due to the project requirements that the server would only be queried for the
domain name given in the arguments.

The DNS server chooses from one of several ip addresses to EC2 servers, which it looks up
using their respective domain names when the server first starts.  At the moment, the
selection process if completely random, since the current goal is to get the CDN
infrastructure working before optimizing server allocation.

The DNS Server was implemented by Nick Jones.

### HTTP Server
A simple HTTP Server was implemented using the BasicHTTPServer Python library.  
The server is given a port and origin server to run on.

The basic caching functionality of our server currently uses a least frequently used algorithm.

The HTTP Server was implemented by Michelle Suk.

### CDN
The deploy script uploads the dns server to /home/$username/dns_server on cs5700cdnproject.ccs.neu.edu.
It also uploads the http server to each of the EC2 servers.

The run script starts the dns and http servers using nohup and catches the output in log files.

The stop script stops the dns and http servers using ```killall -u <username> <process name>```

The CDN deploy/run/stop scripts were implemented by Nick Jones.

## How to Run
To run the DNS Server:
```
./dnsserver -p PORT -n DOMAIN_TO_SERVE
```

To run the HTTP Server:
```
./httpserver -p PORT -o ORIGIN_NAME
```

To deploy/run/stop the full CDN:
```
./[deploy|run|stop]CDN -p <port> -o <origin> -n <name> -u <username> -i <keyfile>
```

## Testing
For the DNS server, we tested using wireshark and dig.
For the HTTP server, we tested using wget.
