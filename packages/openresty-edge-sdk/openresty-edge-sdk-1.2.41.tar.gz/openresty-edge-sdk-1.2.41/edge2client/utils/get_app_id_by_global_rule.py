#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
This file is used to release app
"""

import time
import sys

try:
    import py_client
except ImportError:
    print("Error: cannot import py_client.py")
    exit(1)


def main(action_name):
    client = py_client.get_client()
    app_ids = client.get_all_apps(detail=False)
    global_action_id = client.get_global_action_by_name(action_name)

    not_found = True
    for app_id in app_ids:
        global_actions_rules = client.get_global_actions_used_in_app(app_id)
        if global_action_id in global_actions_rules:
            print("global action {} exists in app: {}."
                  .format(global_action_id, app_id))
            not_found = False

        time.sleep(0.1)

    if not_found:
        print("global action {} not fount in apps.".format(global_action_id))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1]:
        main(sys.argv[1])
    else:
        print('action name required')
