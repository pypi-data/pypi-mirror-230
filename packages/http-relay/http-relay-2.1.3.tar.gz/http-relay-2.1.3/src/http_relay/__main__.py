# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileCopyrightText: Czech Technical University in Prague

from __future__ import print_function

import argparse
import logging
import sys
import threading

from http_relay import HttpRelay


def get_parser():
    parser = argparse.ArgumentParser(
        description="Relay HTTP requests from localhost to a remote host (act as reverse HTTP proxy).")

    parser.add_argument("host", type=str, help='The remote host to connect to (e.g. "cvut.cz")')
    parser.add_argument("port", type=int, default=80, nargs='?',
                        help='The remote host\'s port to connect to (e.g. 80).')
    parser.add_argument("local_port", type=int, default=0, nargs='?',
                        help='The local port to be used for the relay. If left out, will be the same as remote port.')
    parser.add_argument("local_addr", type=str, default='0.0.0.0', nargs='?',
                        help='Local interface (IP or hostname) to run the relay on. By default, it runs on all IPv4 '
                             'interfaces (0.0.0.0).')
    parser.add_argument("-n", "--num-threads", type=int, default=8,
                        help='Number of threads servicing the incoming requests.')
    parser.add_argument("-b", "--buffer-size", type=int, default=1,
                        help='Size of the buffer used for reading responses. Generally, a larger buffer should be more '
                             'efficient, but if it is too large, the local clients may time out before they '
                             'receive any data.')
    parser.add_argument("-t", "--sigkill-timeout", type=int, required=False,
                        help='If specified, the relay will be sigkilled in this number of seconds.')
    parser.add_argument("-s", "--sigkill-on-stream-stop", action="store_true",
                        help='If True, --sigkill-timeout will not be counted when no requests are active, and '
                             'during requests, each successful data transmission will reset the timeout. This can be '
                             'used to detect stale streams if you expect an application to be constantly receiving '
                             'data.')
    return parser


def main(cli_args=None):
    parser = get_parser()
    args = parser.parse_args(cli_args)

    host = args.host.lstrip("[").rstrip("]")  # strip [] from IPv6 addresses
    port = args.port
    local_port = args.local_port if args.local_port != 0 else port
    local_addr = args.local_addr.lstrip("[").rstrip("]")  # strip [] from IPv6 addresses
    num_threads = args.num_threads
    buffer_size = args.buffer_size
    sigkill_timeout = args.sigkill_timeout
    sigkill_on_stream_stop = args.sigkill_on_stream_stop

    logging.info("Relaying HTTP requests from %s:%i to %s:%i using %i threads" % (
        local_addr if ":" not in local_addr else ("[" + local_addr + "]"), local_port,  # wrap IPv6 in []
        host if ":" not in host else ("[" + host + "]"), port,  # wrap IPv6 in []
        num_threads))

    relay = HttpRelay(local_addr, local_port, host, port, buffer_size)

    if sigkill_timeout is not None:
        logging.info("HTTP relay has sigkill timeout set to %i seconds. After that time%s, the node will be killed." % (
            sigkill_timeout, " with a stale stream" if sigkill_on_stream_stop else ""))
        t = threading.Thread(target=relay.sigkill_after, args=(sigkill_timeout, sigkill_on_stream_stop))
        t.daemon = True
        t.start()

    try:
        relay.run(num_threads)
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
