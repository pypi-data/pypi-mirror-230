#!/usr/bin/python

# -*- coding: UTF-8 -*-
"""
This file is used to download emergency nginx.conf from admin server
"""

from urllib.parse import urljoin
from os import environ
import io
import warnings
import requests

try:
    import py_client
except ImportError:
    print("Error: cannot import py_client.py")
    exit(1)

NODE_SERVER = environ.get("NODE_SERVER") \
        or "http://127.0.0.1:8091"
VER_URL = urljoin(NODE_SERVER, "/version")

EMER_PATH = environ.get("EMER_PATH") \
        or "/usr/local/oredge-node/conf/emergency.nginx.conf"


def do_node_server(url):
    res = requests.request("GET", url, timeout=30)

    response = res.json()
    return response


def main():
    data = do_node_server(VER_URL)

    partition = data.get('partition')
    if not partition:
        warnings.warn("no partition found.")
        exit(1)

    client = py_client.get_client()
    data = client.emergency_conf(partition)
    if not isinstance(data, dict):
        print("no ngx_conf found.")
        exit(2)

    ngx_conf = data.get('ngx_conf')
    if not ngx_conf:
        print("no ngx_conf found.")
        exit(3)

    with io.open(EMER_PATH, 'w') as file:
        file.write(ngx_conf)
        print("write to ", EMER_PATH, "... ok.")


if __name__ == '__main__':
    main()
