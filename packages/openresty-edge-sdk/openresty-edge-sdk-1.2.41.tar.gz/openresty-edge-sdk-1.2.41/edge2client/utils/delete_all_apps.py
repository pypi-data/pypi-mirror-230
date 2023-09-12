import os
import sys

from py_client import client

print('delete all apps')
apps = client.get_all_apps()
for app_id in apps:
    ok = client.del_app(app_id)
    if ok:
        print('deleted app: ' + str(app_id))
    else:
        print('failed to delete app: ' + str(app_id))

print('done')

