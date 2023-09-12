#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
update rule condition values.
"""

import json
import argparse

try:
    import py_client
except ImportError:
    print("Error: cannot import py_client.py")
    exit(1)


def main(args):
    client = py_client.get_client()
    client.use_app(args.app_id)

    rules = client.get_all_rules()
    for rule in rules:
        print('{} rule_id: {} {}'.format('-' * 10, rule.get('id'), '-' * 10))
        print(json.dumps(rule))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='query rule_id by app_id')

    parser.add_argument('--app-id', type=int, dest='app_id',
                        help='Application id', required=True)

    args = parser.parse_args()

    main(args)
