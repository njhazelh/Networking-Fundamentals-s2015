#Team the-one-percent
This project was designed according to the standards laid out in 
[Project 1](http://david.choffnes.com/classes/cs4700sp15/project1.php)

##Approach
The idea behind this project was rather simple.  There was little need to
maintain state, and no need to utilize lower level feature such as memory 
management.  What was important was a simple interface with network sockets, the 
ability to easily add SSL/TLS encryption, and strong String parsing ability. 
For this reason, we chose Python as our implementation language.

Our first step was to handle the argument parsing from the command line.  At
first, we attempted to do this using regular expressions, but Python's built-in
arg-parse library turned out to be much simpler.

Next, we implemented a quick method to acquire a configured socket connection.
Python's socket library made this simple, and adding ssl was not much more
difficult.

From here, we only had to handle the message parsing and responses.  To do this,
we wanted to abstract from Strings as quickly as possible.  Therefore, we
implemented a Message class that used regular expressions to match and extract
message parameters into one of several Message sub-classes. Each of these
sub-classes had the same interface, so after converting, all we had to worry
about was calling the do method to react and the isFinal method to check if we
should exit.

##Challenges
The most significant challenge encountered was learning Python. Although we had
some experience working with the language, it took a little work to work out
the structure that used Python in the most appropriate manner.

Additionally, we needed to build the correct regex patterns to match the
messages received.

##Testing
Initially we tested our code by running it as it progressed. After achieving a
functional state, we stabilized the code and added unit tests #TDD.

These tests can be run using "make test" in the project
folder.
