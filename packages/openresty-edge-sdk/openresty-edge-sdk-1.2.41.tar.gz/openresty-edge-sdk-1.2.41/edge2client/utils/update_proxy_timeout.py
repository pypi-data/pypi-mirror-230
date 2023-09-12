#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
This file is used to update proxy timeout & balancer
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
        rules = client.get_all_rules()
        changed = 0

        for rule in rules:
            if 'proxy' not in rule:
                continue

            proxy = rule['proxy']

            need_update = False

            if proxy['connect_timeout'] == 6 \
                    and proxy['connect_timeout_unit'] == 's' \
                    and proxy['read_timeout'] == 6 \
                    and proxy['read_timeout_unit'] == 's' \
                    and proxy['send_timeout'] == 6 \
                    and proxy['send_timeout_unit'] == 's':
                proxy['connect_timeout'] = 30
                proxy['read_timeout'] = 30
                proxy['send_timeout'] = 30

                need_update = True

            if proxy['balancer'] \
                    and proxy['balancer']['algorithm'] == 'roundrobin':
                proxy['balancer_algorithm'] = 'chash'
                proxy['balancer_vars'] = [{'name': 'client-addr'}]

                need_update = True

            if need_update:
                proxy_upstreams = []
                for upstream in proxy['upstream']:
                    proxy_upstreams.append({
                        'upstream': upstream['cluster'],
                        'weight': upstream.get('weight', 1),
                        })

                proxy_backup_upstreams = []
                if 'backup_upstream' in proxy:
                    for upstream in proxy['upstream']:
                        proxy_backup_upstreams.append({'upstream':
                                                       upstream['cluster']})

                proxy_rule = {
                    'upstreams': proxy_upstreams,
                    'backup_upstreams': proxy_backup_upstreams,
                    'retries': proxy.get('retries', 3),
                    'connect_timeout': proxy.get('connect_timeout', 30),
                    'read_timeout': proxy.get('read_timeout', 30),
                    'send_timeout': proxy.get('send_timeout', 30),
                    'retry_condition': proxy.get('retry_condition', None),
                    'balancer_algorithm': proxy.get('balancer_algorithm',
                                                    'roundrobin'),
                    'balancer_vars': proxy.get('balancer_vars', None),
                }

                ok = client.put_rule(rule_id=rule['id'], proxy=proxy_rule)

                if not ok:
                    print("ERROR: failed to update rule, app_id: "
                          + str(app_id))
                else:
                    changed = changed + 1

            time.sleep(0.1)  # for each rule

        if changed > 0:
            print("changed " + str(changed)
                  + " rules for app, id: " + str(app_id))

        time.sleep(0.5)  # for each application


if __name__ == '__main__':
    main()
