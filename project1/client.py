#!/usr/bin/python

import re
import argparse
import socket
import ssl

import messages


__author__ = 'Nick Jones'


def model_data(data):
    statusRegex = re.compile("cs5700spring2015 STATUS (\d+) ([\+,\-,\*,\/]) (\d+)\n")
    result = statusRegex.match(data)
    if result is not None:
        return messages.StatusMessage(int(result.group(1)), result.group(2), int(result.group(3)))
    else:
        byeRegex = re.compile("cs5700spring2015 (.*) BYE\n")  # TODO: figure out regex for 64 bytes.  [A-F,0-9]{64}
        return messages.ByeMessage(byeRegex.match(data).group(1))


def parse_message(conn, data):
    """
    This function will find which type of message the data is and create a response.
    :param data: The data from the server
    :return:
    """
    message = model_data(data)
    message.do(conn)
    return message.isFinal()


def make_connection(secure, hostname, port):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if secure:
        conn = ssl.wrap_socket(conn)
    conn.connect((hostname, port))
    return conn


def send_recv_loop(conn):
    while True:
        final = parse_message(conn, conn.read(256))
        if final:
            break


def main(args):
    """
    This is the entry point for the program.

    To run the program, run the following in the command line.
        ./client <-p port> <-s> [hostname] [NEU ID]

    Run "./client -h" for more info

    :return: Return nothing.
    """
    conn = make_connection(args.secure, args.hostname, args.port)
    conn.write("cs5700spring2015 HELLO {}\n" % args.id)
    send_recv_loop(conn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Do lots of meaningless math over the network!")
    parser.add_argument("-p", "--port", help="The server port to connect to", type=int, default=27993)
    parser.add_argument("-s", "--secure", help="Use a secure socket", action='store_true')
    parser.add_argument("hostname", help="The hostname of the server")
    parser.add_argument("id", help="The NEU id of the student running the program.  Must have all leading zeros.")
    args = parser.parse_args()
    main(args)
