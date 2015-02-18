from CookieCache import CookieCache

__author__ = 'njhazelh'

from Exceptions import BadHeaderException, BadStatusException, EmptySocketException, MissingHeaderException
import logging

log = logging.getLogger("webcrawler")


class HTTP_STATUS:
    OK = 200
    MOVED_PERM = 301
    FOUND = 302
    FORBIDDEN = 403
    NOT_FOUND = 404
    SERVER_ERROR = 500


class HttpServerMessage:
    def __init__(self, sock):
        self.version = ""
        self.headers = {}
        self.body = ""
        self.status_code = None
        self.cookies = CookieCache()
        self._getMessage(sock)

    def _getMessage(self, sock):
        """
        Read the headers and body into this structure from the network.
        :param sock: A HttpSocket containing a server response
        """
        file = sock.get_socket().makefile("rb")
        self._read_status(file)
        self._read_headers(file)

        if self.safe_get_header("transfer-encoding") == "chunked":
            self._read_chunked(file)
        else:
            self._read_body(int(self.get_header("content-length")), file)
        file.close()

    def _read_status(self, file):
        status = file.readline().decode("utf-8")

        if not status:
            raise EmptySocketException()
        try:
            version, status_code, status = status.strip().split(None, 2)
            self.version = version
            self.status_code = int(status_code)
            self.reason = status
        except ValueError:
            raise BadStatusException(status)

    def _read_headers(self, file):
        key = ""
        while True:
            line = file.readline()

            if line is None:
                raise EmptySocketException()

            line = line.decode("utf-8")

            if ":" not in line:
                break

            stripped = line.strip()

            if line[0] is " ":
                self._add_header(key, stripped)
                continue

            try:
                key, value = stripped.split(": ", 1)
                self._add_header(key, value)
            except ValueError:
                raise BadHeaderException(line)


    def _add_header(self, key, value):
        key = key.lower()

        if key == "set-cookie":
            self.cookies.set_cookie(value)

        if key in self.headers.keys():
            current_val = self.headers[key]
            current_val = current_val + ", " + value
            self.headers[key] = current_val
        else:
            self.headers[key] = value

    def _read_body(self, size, file):
        data = ""
        while size > 0:
            new_data = file.read(size)
            if new_data is None:
                raise EmptySocketException()
            new_data = new_data.decode("utf-8")
            size -= len(new_data)
            data += new_data
        self.body = data

    def _read_chunked(self, file):
        log.debug("Reading a chunked message")
        body = ""
        while True:
            size_line = file.readline()
            if size_line is None:
                raise EmptySocketException()
            size_line = size_line.decode("utf-8").strip()
            size = int(size_line, 16)
            if size == 0:
                break
            data = ""
            while size > 0:
                new_data = file.read(size)
                if new_data is None:
                    raise EmptySocketException()
                new_data = new_data.decode("utf-8")
                size -= len(new_data)
                data += new_data
            body += data
            file.read(2)  # read line \r\n
        self.body = body
        self._read_headers(file)


    def get_header(self, key):
        try:
            return self.headers[key]
        except KeyError:
            raise MissingHeaderException(key)

    def safe_get_header(self, key):
        if key in self.headers.keys():
            return self.get_header(key)
        else:
            return ""

    def __str__(self):
        status = "{} {} {}".format(self.version, self.status_code, self.reason)
        headers = "\r\n".join(["{}: {}".format(key, self.headers[key]) for key in self.headers])
        return "\r\n".join([status, headers, "", self.body])
