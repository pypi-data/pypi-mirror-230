# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileCopyrightText: Czech Technical University in Prague

"""
Relay HTTP get requests from localhost to a remote host (act as reverse HTTP proxy).
"""

import errno
import logging
import os
import signal
import socket
import sys
import threading
import time

from functools import partial

try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from http.client import *
except ImportError:
    from SimpleHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from httplib import HTTPConnection


__all__ = ['HttpRelay']


# Some servers (e.g. NTRIP, Shoutcast...) do respond with nonstandard status lines like "ICY 200 OK" instead of
# the standard "HTTP/1.0 200 OK". The Python 3 client raises an exception when it finds these status lines.
# Python 2 client works fine, but overrides the status line to HTTP/1.0. What we want instead is to tell the rest
# of the codebase to look at such response as HTTP/1.0 response, but save the original status line so that it can
# be relayed exactly as it was received.

# Code borrowed and modified from Python 3 source code available under the Python Software Foundation License.
class NonstandardHttpResponse(HTTPResponse):
    def _read_status(self):
        _MAXLINE = 65536
        if sys.version_info.major > 2:
            line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
        else:
            line = self.fp.readline(_MAXLINE + 1)
        if len(line) > _MAXLINE:
            raise LineTooLong("status line")
        if self.debuglevel > 0:
            print("reply:", repr(line))
        if not line:
            # Presumably, the server closed the connection before
            # sending a valid response.
            if sys.version_info.major > 2:
                raise RemoteDisconnected("Remote end closed connection without"
                                         " response")
            else:
                raise BadStatusLine("No status line received - the server "
                                    "has closed the connection")
        self._status_line = line
        try:
            version, status, reason = line.split(None, 2)
        except ValueError:
            try:
                version, status = line.split(None, 1)
                reason = ""
            except ValueError:
                # empty version will cause next test to fail.
                version = ""
        if not version.startswith("HTTP/"):
            # Here is the difference to the original method: we treat invalid version as HTTP 1.0
            version = "HTTP/1.0"

        # The status code is a three-digit number
        try:
            status = int(status)
            if status < 100 or status > 999:
                raise BadStatusLine(line)
        except ValueError:
            raise BadStatusLine(line)
        return version, status, reason


class HTTP10Connection(HTTPConnection):
    _http_vsn_str = "HTTP/1.0"
    _http_vsn = 10
    response_class = NonstandardHttpResponse


class HTTP11Connection(HTTPConnection):
    _http_vsn_str = "HTTP/1.1"
    _http_vsn = 11
    response_class = NonstandardHttpResponse


def is_server_running(server):
    try:
        return server.running
    except:
        return not server._BaseServer__shutdown_request


class Handler(BaseHTTPRequestHandler):
    """
    The main logic of the relay - forward the HTTP request to the remote server with changed Host: header and pass back
    whatever it returns.
    """
    def __init__(self, relay, request, client_address, server):
        self._req_num = relay.request_num
        relay.request_num += 1

        self.relay = relay
        self.host = relay.host
        self.port = relay.port
        self.relay_port = relay.relay_port
        self.read_buffer_size = relay.read_buffer_size

        try:
            BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        except socket.error as e:
            self.log_socket_error(e)

    # Do not log requests using the BaseHTTPRequestHandler logging mechanism, we have our own.
    def log_request(self, code='-', size='-'):
        pass

    def log_error(self, format, *args):
        """
        Log an error message.
        :param str format: Format string.
        :param List[Any] args: % parameters of the format string.
        """
        if not self.relay.shutting_down and is_server_running(self.server):
            logging.error(("Request [%i] error: " + format) % ((self._req_num,) + args))

    def log_socket_error(self, e):
        """
        Log an error raised by socket operation.
        :param socket.error e: The error.
        """
        # Ignore EPIPE and ECONNRESET as that is generated when the other end stops being interested in our data
        if isinstance(e, tuple) and e[0] in (errno.EPIPE, errno.ECONNRESET):
            logging.info("Response [%i]: finished" % (self._req_num,))
        elif ("Errno %i" % (errno.EPIPE,)) in str(e) or ("Errno %i" % (errno.ECONNRESET,)) in str(e):
            logging.info("Response [%i]: finished" % (self._req_num,))
        else:
            if not self.relay.shutting_down and is_server_running(self.server):
                self.log_error("%s", str(e))

    def log_message(self, format, *args):
        """
        Log an info message.
        :param str format: Format string.
        :param List[Any] args: % parameters of the format string.
        """
        if is_server_running(self.server):
            logging.info(("Request [%i]: " + format) % ((self._req_num,) + args))

    def log_response(self, format, *args):
        """
        Log an info message related to the response.
        :param str format: Format string.
        :param List[Any] args: % parameters of the format string.
        """
        if is_server_running(self.server):
            logging.info(("Response [%i]: " + format) % ((self._req_num,) + args))

    def send_status_line(self, response):
        self.log_request(response.status)
        if self.request_version != 'HTTP/0.9':
            if sys.version_info[0] > 2:
                # self.send_response_only(code, message)
                if not hasattr(self, '_headers_buffer'):
                    self._headers_buffer = []
                self._headers_buffer.append(response._status_line.encode('latin-1', 'strict'))
            else:
                self.wfile.write(response._status_line)

    def do_GET(self):
        """
        Do the relaying work.
        """
        with self.relay.lock:
            self.relay.num_open_requests += 1
        try:
            # Choose the right HTTP version
            connection_class = HTTP11Connection if self.protocol_version == "HTTP/1.1" else HTTP10Connection
            conn = connection_class(self.host, self.port)

            # Forward the request with the same headers
            headers = dict(zip(self.headers.keys(), self.headers.values()))

            # Replace host in Host header
            orig_host = None
            host = self.host if ":" not in self.host else ("[" + self.host + "]")
            host_port = host
            for header in headers:
                if header.lower() == "host":
                    orig_host = headers[header]
                    # append port if it is non-default or if it differs from the relay port
                    if self.port != 80 and (self.port != self.relay_port or ":" in orig_host):
                        # : is also valid in IPv6 addresses; a port is specified in an IPv6 only if the last : is after
                        # the last ]
                        if not (":" in orig_host and "]" in orig_host) or (orig_host.rfind(':') > orig_host.rfind(']')):
                            host_port += ":" + str(self.port)
                    headers[header] = host_port
                    break

            self.log_message("GET http://%s%s", host_port, self.path)
            conn.request("GET", self.path, headers=headers)

            # Obtain the response
            resp = conn.getresponse()
            self.send_status_line(resp)
            self.log_response("%i %s", resp.status, resp.reason)

            # Forward back the response headers
            for header, value in resp.getheaders():
                # Replace host in Location header
                if orig_host is not None and header.lower() == "location":
                    value = value.replace(host, orig_host, 1)
                self.send_header(header, value)
            self.end_headers()

            # Forward back the response body
            num_bytes = 0
            while True:
                chunk = resp.read(self.read_buffer_size)
                if not chunk:
                    self.log_response("finished")
                    break
                self.wfile.write(chunk)
                num_bytes += self.read_buffer_size
                self.relay.total_bytes += self.read_buffer_size
                if num_bytes > 10 * self.read_buffer_size:
                    logging.debug("Response body [%i]: Sent %i bytes." % (self._req_num, num_bytes))
        except socket.error as e:
            self.log_socket_error(e)
        except KeyboardInterrupt:
            pass
        #except Exception as e:
        #    self.log_error("%s", str(e))
        finally:
            with self.relay.lock:
                self.relay.num_open_requests -= 1


class Thread(threading.Thread):
    """
    The HTTP server servicing thread.
    """

    def __init__(self, server, relay):
        """
        Create and run the servicing thread.
        :param HTTPServer server: The server to work with.
        :param HttpRelay relay: The relay.
        """
        threading.Thread.__init__(self)
        self.server = server
        self.relay = relay
        self.daemon = True
        self.start()

    def run(self):
        """
        Process the server requests.
        """
        try:
            self.server.serve_forever()
        except Exception as e:
            if not self.relay.shutting_down and is_server_running(self.server):
                logging.error("Error in processing thread: " + str(e))


class HttpRelay(object):
    """
    Relay HTTP get requests from localhost to a remote host (act as reverse HTTP proxy).
    """

    def __init__(self, relay_addr, relay_port, remote_host, remote_port, buffer_size):
        """
        Run the multithreaded relay server.
        :param str relay_addr: IP address or hostname specifying the local interface(s) to run the relay on
                               (pass 0.0.0.0 or :: to run it on all interfaces (IPv4 or IPv6)).
        :param int relay_port: The local port.
        :param str remote_host: The remote host name.
        :param int remote_port: The remote host port.
        :param int buffer_size: Size of the buffer used for reading responses. If too large, the forwarding can be too slow.
        """
        self.server_address = (relay_addr.lstrip("[").rstrip("]"), relay_port)
        self.host = remote_host.lstrip("[").rstrip("]")
        self.port = remote_port
        self.relay_port = relay_port
        self.read_buffer_size = buffer_size

        self.request_num = 0
        self.total_bytes = 0
        self.num_open_requests = 0
        self.shutting_down = False
        self.lock = threading.Lock()

        # Create a standalone socket shared by all servers
        socket_type = socket.AF_INET if ":" not in relay_addr else socket.AF_INET6
        self.socket = socket.socket(socket_type, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self, num_threads=1):
        """
        Run the multithreaded relay server.
        :param int num_threads: Number of servicing threads.
        """
        try:
            self.socket.bind(self.server_address)
            self.socket.listen(5)

            # Create the servers and run their servicing threads
            servers = []
            threads = []
            for i in range(num_threads):
                handler = partial(Handler, self)
                httpd = HTTPServer(self.server_address, handler, False)
                httpd.socket = self.socket
                httpd.server_bind = httpd.server_close = lambda self: None
                servers.append(httpd)
                threads.append(Thread(httpd, self))

            # Wait for node exit
            try:
                while not self.shutting_down:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                pass

            logging.info("Stopping HTTP relay.")

            self.shutting_down = True

            # First, shut down the socket, which should convince server.shutdown() to finish.
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()

            # Shut down the servers (their service threads are daemons, so we don't need to join them)
            for server in servers:
                if server is not None:
                    server.shutdown()

        except socket.gaierror as e:
            logging.error(str(e))
            self.shutting_down = True
            raise
        except socket.error as e:
            logging.error(str(e))
            self.shutting_down = True
            raise
        except:
            self.shutting_down = True
            raise

    def shutdown(self):
        self.shutting_down = True

    def sigkill_after(self, timeout, check_streaming=False):
        remaining = timeout
        last_total_bytes = -1
        while not self.shutting_down:
            if not check_streaming or (self.num_open_requests > 0 and self.total_bytes == last_total_bytes):
                remaining -= 1
                if remaining <= 0:
                    logging.error("Stopping HTTP relay!")
                    self.shutting_down = True
                    time.sleep(0.01)
                    os.kill(os.getpid(), signal.SIGKILL)
                    return
            else:
                remaining = timeout
            if check_streaming and remaining == timeout // 2:
                logging.warning(
                    "Relayed HTTP stream stopped. The relay will be stopped in %i sec if the stream does not "
                    "resume." % (timeout // 2,))
            last_total_bytes = self.total_bytes
            time.sleep(1)
