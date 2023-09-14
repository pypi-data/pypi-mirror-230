<!--
SPDX-License-Identifier: BSD-3-Clause
SPDX-FileCopyrightText: Czech Technical University in Prague
-->

# http-relay

Relay HTTP requests from localhost to a remote host (act as reverse HTTP proxy).

This HTTP relay properly processes also the nonstandard HTTP responses like `ICY 200 OK` produced by Shoutcast or NTRIP streaming servers.

The relay works properly with hostnames, IPv4 and IPv6 addresses. IPv6 addresses can be specified with or without `[]`. 

## Usage

```
usage: http-relay [-h] [-n NUM_THREADS] [-b BUFFER_SIZE] [-t SIGKILL_TIMEOUT] [-s] host [port] [local_port] [local_addr]

positional arguments:
  host                  The remote host to connect to (e.g. "cvut.cz")
  port                  The remote host's port to connect to (e.g. 80).
  local_port            The local port to be used for the relay. If left out, will be the same as remote port.
  local_addr            Local interface (IP or hostname) to run the relay on. By default, it runs on all IPv4 interfaces (0.0.0.0).

optional arguments:
  -h, --help            show this help message and exit
  -n NUM_THREADS, --num-threads NUM_THREADS
                        Number of threads servicing the incoming requests.
  -b BUFFER_SIZE, --buffer-size BUFFER_SIZE
                        Size of the buffer used for reading responses. Generally, a larger buffer should be more efficient, but if it is too large, the local clients may time out before they receive any data.
  -t SIGKILL_TIMEOUT, --sigkill-timeout SIGKILL_TIMEOUT
                        If specified, the relay will be sigkilled in this number of seconds.
  -s, --sigkill-on-stream-stop
                        If True, --sigkill-timeout will not be counted when no requests are active, and during requests, each successful data transmission will reset the timeout. This can be used to detect
                        stale streams if you expect an application to be constantly receiving data.

```

## Python module

This package also provides Python module `http_relay`. You can start the relay as a part of your application like this:

```python
from http_relay import run

# ...

run("0.0.0.0", 80, "cvut.cz", 80)
```

## Examples

```bash
http-relay cvut.cz 80 8080  # redirects local port 8080 to cvut.cz:80
http-relay cvut.cz 2101  # redirects local port 2101 to cvut.cz:2101
http-relay cvut.cz 80 8080 localhost  # redirects localhost:8080 to cvut.cz:80 (i.e. no external access to the 8080 port)

http-relay stream.cz 2101 -t 10 -s  # redirects local port 2101 to stream.cz and kills the relay after 10 secs if a stream is being downloaded and becomes stale
```