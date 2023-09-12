#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
This file is used to release app pending_changes
"""

import argparse

try:
    import py_client
except ImportError:
    print("Error: cannot import py_client.py")
    exit(1)


def main(args):
    app_id = args.app_id

    client = py_client.get_client()
    client.use_app(app_id)

    pending_changes = client.pending_changes()

    if args.dry_run:
        print('app {}: pending_changes: {}'.format(app_id, pending_changes))
        return

    ret = client.new_release()
    if ret:
        print('app {}: release ok: {} changes.'
              .format(str(app_id), pending_changes))
    else:
        print('app {}: release failed'.format(str(app_id)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='release app pending changes.')

    parser.add_argument('--dry-run',
                        dest='dry_run',
                        action='store_true',
                        help='dry run.')
    parser.add_argument('--app-id',
                        dest='app_id',
                        type=int,
                        required=True,
                        help='specifiy the app_id to operate on.')

    args = parser.parse_args()

    main(args)
