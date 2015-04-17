# Project 5: CDN
Nick Jones, Michelle Suk

## Overview
This project involves the creation of a Content Distribution Network (CDN).

## Components
### DNS Server
The DNS Server is pretty simple.  It is given a domain name and a port to run on.
All requests that it receives, it responds to with the same response.

In the future, it will decide which HTTP Server will best serve the client.
For the moment, it just returns 127.0.0.1

The DNS Server was implemented by Nick Jones.

### HTTP Server
The HTTP Server was implemented by Michelle Suk.

### CDN
Not Implemented Yet

## How to Run
To run the DNS Server:
```
./dnsserver -p PORT -n DOMAIN_TO_SERVE
```

## Testing
For the DNS server, we tested using wireshark and dig.
