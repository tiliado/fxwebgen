# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

from http.server import SimpleHTTPRequestHandler, HTTPServer
from typing import Optional

DEFAULT_PORT = 8000
DEFAULT_HOST = '127.0.0.1'


def serve(host: Optional[str] = None, port: Optional[int] = None) -> None:
    address = (host or DEFAULT_HOST, port or DEFAULT_PORT)
    httpd = HTTPServer(address, SimpleHTTPRequestHandler)
    print(f'Serving on http://{address[0]}:{address[1]} ...')
    httpd.serve_forever()
