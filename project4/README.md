# Networking Fundamentals: Project 4
Nick Jones, Michelle Suk

## Overview
This project requires the implementation of IP, TCP, and HTTP.

The approach of this project was to create an interface similar to
sockets for TCP and IP.  We realized that this meant that TCP and IP
had to run on separate threads so they could aquire and parse data
in real time.

The first step in our approach was to create TCP and IP Packet objects,
these allowed us to isolate the data -> bytes and bytes -> data processes
from the rest of the code.  The other part was TCP and IP Socket objects,
these ran an infinite loop within their own thread, so they could get and
parse packets in real-time.  They interacted with other threads via
Python's thread-safe Queue module, which we use to store input and output
data until it was needed.

We used the HTTP code from project 2, because it was functional, and
it was generic enough the it wasn't hard to apply.  We only needed
the HTTP GET method, so a lot of the functionality is latent.

## Issues Encountered
Several issues were encountered during this project.

First, we couldn't get the check-sums to work correctly for a while.

Next, we couldn't get the packets from the server to ACK correctly,
so they just repeated endlessly.  It turned out that we were needlessly
adding 1 to what the actual number was.

Additionally, we encountered an annoying bug, where the server would
continue to spam us after Ctrl+C ing the program.  This meant that
everything slowed down, wire-shark got bogged down, and data was harder
to understand.  After putting up with it for a while by restarting our
VM every so often, we discovered we could stop it by removing the
iptables DROP RST rule temporarily.

Finally, we couldn't get the ip address of our source using the common
socket.gethostbyname(socket.gethostname()), because this mapped to
127.0.1.1 in our hosts file.  Instead we had to query the OS for the
ip address of eth0.

## Work Division
Nick completed the IP by himself.

Michelle started the TCP, but after little to no progress, and with the
approaching deadline, Nick also implemented TCP.

Nick also implemented the overlying application, including input parsing,
HTTP, and file saving.

Michelle wrote some documentation.

## Running the Code
Run the code using the following command.
```
sudo ./rawhttpget <HTTP URL>
```

Since the code relies on RAW sockets, it must be run under sudo.  Otherwise,
it will encounter permission issues.

Additionally, the kernel doesn't like people sending it packets when it doesn't
think that it has any TCP connections on a port.  As a result, it sends
RST packets to hosts that do so, which would kill any connections you wish to make.

The solution to this problem is to run
```
sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP
```
This will tell iptables to filter any outgoing RST packets.

Once you have finished using raw sockets, the following code will remove
the filter. Note, this assumes you only have one rule in iptables OUTPUT.
```
sudo iptables -D OUTPUT 1
```
To see all current rules, run:
```
sudo iptables -L
```

__NOTE: ```./rawhttpget <URL>``` will run these automatically.__

## Components
### HTTP
Adapted from Project 2.  Only the GET method was needed.  Additionally,
we made some small modifications so it could get byte_code rather than
just utf-8 text.

### TCP
TCP incorporates a sliding window, and slow start.  It runs in a separate
thread, so that it can respond to packets in real-time. Sending data wasn't
as important for this application, since GET doesn't have a body and is a
relatively short message that's only sent once.  However, we did implement
RTT and retransmit with slow start.  It also remembers all mis-ordered packets
so that it can recall them when the missing packet arrives.

### IP
IP also runs in it's own thread.

## Testing
This code was debugged using wire-shark throughout the development process.
This enabled us to verify our checksum implementation, and understand why
packets were not flowing correctly.

Additionally, after the program was finished we ran it on the same files
as wget, and compared the results using cmp and diff.  The results were
exactly the same, and we obtained them in approximately the same time.
