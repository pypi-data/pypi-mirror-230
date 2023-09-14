# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileCopyrightText: Czech Technical University in Prague

"""
Integration test testing the relay functionality.
"""

import http_relay
import socket
import threading
import time
import unittest

from http_relay.__main__ import main

try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from http.client import *
except ImportError:
    from SimpleHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from httplib import HTTPConnection


class TestHandler(BaseHTTPRequestHandler):
    __test__ = False

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Test")


class NTRIPHandler(BaseHTTPRequestHandler):
    """This handler simulates NTRIP server responses which use a slight
    modification of the HTTP protocol."""
    def do_GET(self):
        self.wfile.write(b"ICY 200 OK\r\n")
        if not hasattr(self, '_headers_buffer'):
            self._headers_buffer = []
        self.end_headers()
        self.wfile.write(b"Test")


class TestServer(threading.Thread):
    __test__ = False

    def __init__(self, host, port, handler=TestHandler):
        """
        Create and run the test server thread.
        :param str host: The host to listen on.
        :param int port: The port to listen on.
        """
        threading.Thread.__init__(self)
        HTTPServer.address_family = \
            socket.AF_INET if ":" not in host else socket.AF_INET6
        self.server = HTTPServer((host, port), handler)
        self.daemon = True
        self.running = False
        self.start()

    def run(self):
        """
        Process the server requests.
        """
        try:
            self.running = True
            self.server.serve_forever()
        except Exception:
            pass


class RelayThread(threading.Thread):

    def __init__(self, host, server_port, relay_port, use_main=False):
        """
        Create and run the test relay. All args are passed to `run()`.
        """
        threading.Thread.__init__(self)
        self.host = host
        self.server_port = server_port
        self.relay_port = relay_port
        self.use_main = use_main
        self.relay = None
        self.daemon = True
        self.running = False
        self.start()

    def run(self):
        """
        Process the server requests.
        """
        self.running = True
        if self.use_main:
            cli_args = list(map(str, [
                self.host, self.server_port, self.relay_port, self.host,
                "--num-threads", 1
            ]))
            main(cli_args)
        else:
            self.relay = http_relay.HttpRelay(self.host, self.relay_port,
                                              self.host, self.server_port, 1)
            self.relay.run(num_threads=1)

    def stop(self):
        if self.relay is not None:
            self.relay.shutdown()


def get_response_body(resp):
    resp_body = b""
    while True:
        chunk = resp.read(1)
        if not chunk:
            break
        resp_body += chunk
    return resp_body


class TestRelay(unittest.TestCase):
    def test_local_relay_hostname(self):
        self.do_test('localhost', 8080, 8081)

    def test_local_relay_ipv4(self):
        self.do_test('127.0.0.1', 8040, 8041)

    def test_local_relay_ipv6(self):
        self.do_test('::1', 8060, 8061)

    def test_local_relay_ipv6_brackets(self):
        self.do_test('[::1]', 8050, 8051, "::1")

    def test_local_relay_ntrip(self):
        self.do_test('localhost', 2101, 2102, handler=NTRIPHandler)

    def test_main(self):
        self.do_test('localhost', 8090, 8091, use_main=True)

    def do_test(self, host, server_port, relay_port, server_host=None,
                use_main=False, handler=TestHandler):
        if server_host is None:
            server_host = host
        server_thread = TestServer(server_host, server_port, handler=handler)
        relay_thread = RelayThread(
            host, server_port, relay_port, use_main=use_main)

        while not server_thread.running or not relay_thread.running:
            time.sleep(0.01)
        time.sleep(1.0)

        if not issubclass(handler, TestHandler):
            HTTPConnection.response_class = \
                http_relay.relay.NonstandardHttpResponse
        conn = HTTPConnection(server_host, relay_port, timeout=1.0)
        conn.request("GET", "test")
        resp = conn.getresponse()

        relay_thread.stop()

        self.assertEqual(200, resp.status)

        resp_body = get_response_body(resp)

        self.assertEqual(b"Test", resp_body)

    def test_concurrent(self):
        server_host = "localhost"
        host = "localhost"
        server_port = 8100
        server_thread = TestServer(server_host, server_port, handler=TestHandler)
        relay_thread1 = RelayThread(host, server_port, 8101)
        relay_thread2 = RelayThread(host, server_port, 8102)

        while not server_thread.running or not relay_thread1.running or not relay_thread2.running:
            time.sleep(0.01)
        time.sleep(1.0)

        conn1 = HTTPConnection(server_host, 8101, timeout=1.0)
        conn1.request("GET", "test")
        resp1 = conn1.getresponse()

        conn2 = HTTPConnection(server_host, 8102, timeout=1.0)
        conn2.request("GET", "test")
        resp2 = conn2.getresponse()

        relay_thread1.stop()

        self.assertEqual(200, resp1.status)
        self.assertEqual(200, resp2.status)

        resp1_body = get_response_body(resp1)
        resp2_body = get_response_body(resp2)
        self.assertEqual(b"Test", resp1_body)
        self.assertEqual(b"Test", resp2_body)

        time.sleep(1.0)

        conn3 = HTTPConnection(server_host, 8102, timeout=1.0)
        conn3.request("GET", "test")
        resp3 = conn3.getresponse()

        relay_thread2.stop()

        self.assertEqual(200, resp3.status)

        resp3_body = get_response_body(resp3)
        self.assertEqual(b"Test", resp3_body)


if __name__ == '__main__':
    unittest.main()
