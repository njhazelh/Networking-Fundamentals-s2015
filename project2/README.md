#Networking Fundamentals: Project 2: Webcrawler
####Nick Jones, Michelle Suk

##Overview
This project is a simple web-crawler that uses HTTP to find a series of
5 secret keys hidden throughout Fakebook.

##Problems
The biggest issue encountered was that we didn't know
how big the HTTP message would be, so we couldn't create a
fixed size buffer and read from the socket.  Instead, we
had to read line by line from the socket, recording header
values until the header was over.  At this point we knew
we would have the Content-length header, so we could
read that many bytes.

##Running
To run run `./webcrawler [username] [password]`

##Testing
To test, run `make test`
