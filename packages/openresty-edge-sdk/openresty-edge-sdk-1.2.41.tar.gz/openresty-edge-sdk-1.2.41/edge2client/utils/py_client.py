#!/usr/bin/python
# -*- coding: UTF-8 -*-
""" python style config file
This file is used to export common config
"""

from os import environ, getcwd, path
import sys

HOST = 'https://127.0.0.1:443'
USER = 'admin'
PASSWORD = 'edge@password'
SSL_VERIFY = False
PYTHON_SDK_DIR = path.join(getcwd(), '/usr/local/oredge-python-sdk/lib')
APPS_DIR = path.join(getcwd(), './apps')


def get_client():
    python_sdk_dir = environ.get('EDGE_PYTHON_DIR') \
        or PYTHON_SDK_DIR
    sys.path.append(python_sdk_dir)
    from edge2client import Edge2Client

    host = environ.get('EDGE_HOST') or HOST
    user = environ.get('EDGE_USER') or USER
    password = environ.get('EDGE_PASSWORD') or PASSWORD
    ssl_verify = environ.get('EDGE_SSL_VERIFY') or SSL_VERIFY

    print('--------- config file ----------\n'
          'edge-admin host: {}\n'
          'edge-admin user: {}\n'
          'edge-admin ssl_verify: {}\n'
          'edge-admin apps_dir: {}\n'
          'edge-admin python_sdk_dir: {}\n'
          '========= runtime =============='
          .format(host, user, ssl_verify, APPS_DIR, python_sdk_dir))

    client = Edge2Client(host, user, password)
    client.set_ssl_verify(ssl_verify)
    client.login()

    return client


def get_apps_dir():
    return APPS_DIR


if __name__ == '__main__':
    print('This statement will be executed only '
          'if this script is called directly')
