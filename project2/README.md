#Networking Fundamentals: Project 2: Webcrawler
####Nick Jones, Michelle Suk

##Overview
This project is a simple web-crawler that uses HTTP to find a series of
5 secret keys hidden throughout Fakebook.

##Approach
Our approach was to abstract things away as much as possible.
On the top level, we build a Strategy object that was responsible
for the search algorithm and flag finding.  This object
interacted directly with the Browser object, which would
take HttpClientMessages and return HttpServerMessages.
HttpClientMessages and HttpServerMessages were models that
encapulated the formulation and parsing of message strings.
Finally, we used a HttpSocket to abstract away the lowest
level of the sockets.  It was originally intended that
we could re-implement HttpSocket to be multi-threaded; however, 
due to time constraints, we were unable to do so.  We find that
our program usually runs in 4-10 minutes depending on network
load.

##Problems
The biggest issue encountered was that we didn't know
how big the HTTP message would be, so we couldn't create a
fixed size buffer and read from the socket.  Instead, we
had to read line by line from the socket, recording header
values until the header was over.  At this point we knew
we would have the Content-length header, so we could
read that many bytes.  This was especially an issue
with the chunked messages.

We encountered a brief problem with BeautifulSoup,
because the CCIS computers only have 4.0, whereas
we were using 4.3.  This meant that a feature we
were using to find flags wasn't available.

##Running
This will run the code with INFO level verbosity
for both partners.
To run run `./webcrawler [username] [password]`

##Testing
To test, run `make test`

Our program is sufficiently modular that we
were able to unit test individual pieces as
we build them.

For other parts and the entire program, which
relies on network interaction, we used Wireshark
to observe traffic.

Finally, we integrated log statements throughout
our code.  These can be activated using an
optional argument `[-v DEBUG|INFO|WARN|ERROR|CRITICAL]`
