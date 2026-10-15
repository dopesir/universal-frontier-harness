#!/usr/bin/env python3
"""Managed background HTTP preview server.

Serves static or build directories with automatic port discovery,
enforcing Rule 20 (interactive web ergonomics).
"""

from __future__ import annotations

import argparse
import functools
import http.server
import os
import socket
import socketserver
import sys
from pathlib import Path


def find_free_port(start_port: int = 8080, max_attempts: int = 50) -> int:
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start_port


def main():
    parser = argparse.ArgumentParser(description="Live Preview HTTP Server")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to serve")
    parser.add_argument("--port", type=int, default=8080, help="Preferred port")
    args = parser.parse_args()

    serve_dir = Path(args.directory).resolve()
    port = find_free_port(args.port)

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(serve_dir))

    # Allow fast address reuse
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        print(f"PREVIEW_READY: http://localhost:{port}")
        print(f"SERVING_DIR: {serve_dir}")
        sys.stdout.flush()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer terminated.")


if __name__ == "__main__":
    main()
