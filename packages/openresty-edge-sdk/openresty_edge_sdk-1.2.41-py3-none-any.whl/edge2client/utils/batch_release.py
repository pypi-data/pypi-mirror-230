#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
This file is used to release app
"""

import time

try:
    import py_client
except ImportError:
    print("Error: cannot import py_client.py")
    exit(1)


def main():
    client = py_client.get_client()
    app_ids = client.get_all_apps(detail=False)

    for app_id in app_ids:
        client.use_app(app_id)
        ret = client.new_release()
        if ret:
            print('release ok app_id: ' + str(app_id))
        else:
            print('release failed: ' + str(app_id))
        time.sleep(0.1)



if __name__ == '__main__':
    main()
