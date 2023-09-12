#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
update app's upstream weight
"""

import argparse

try:
    import py_client
except ImportError:
    print("Error: cannot import py_client.py")
    exit(1)


def main(args):
    if not args.upstream_ip and not args.upstream_domain:
        print('--upstream_ip or --upstream_domain must be specified')
        exit(1)

    # init
    client = py_client.get_client()

    # search upstreams
    upstreams = []
    search_item = ''
    search_val = ''

    if args.upstream_ip:
        upstreams = client.search_app(upstream_ip=args.upstream_ip)
        search_item = 'ip'
        search_val = args.upstream_ip
    elif args.upstream_domain:
        upstreams = client.search_app(upstream_domain=args.upstream_domain)
        search_item = 'domain'
        search_val = args.upstream_domain

    nups = len(upstreams)

    upstream = {}
    upstream_id = args.upstream_id

    if nups == 0:
        print('upstream not found by {}: {}'.format(search_item, search_val))
        exit(1)
    elif nups == 1:
        upstream = upstreams[0]
    else:
        if not upstream_id:
            print('results are not uniq by {}: {}\n'
                  'please use --upstream_id to determine the upstream'
                  .format(search_item, search_val))

            for up in upstreams:
                app_name = ''
                app = up.get('app')
                if app:
                    app_name = app.get('name')

                print('id: {}, name: {}, app_name: {}'
                      .format(up.get('id'), up.get('name'), app_name))

            exit(1)

        for up in upstreams:
            if up.get('id') == upstream_id:
                upstream = up

        if not upstream or upstream.get('id') != upstream_id:
            print('upstream not found by upstream_id: {}'.format(upstream_id))
            exit(1)

    app = upstream.get('app')
    if not app:
        print('cannot update upstream without app')
        exit(1)

    app_id = app.get('id')
    client.use_app(app_id)

    servers = []

    upstream_obj = client.get_upstream(upstream.get('id'))
    old_servers = upstream_obj.get('nodes')
    for s in old_servers:
        server = {}
        for k in s:
            if k.startswith('_'):
                continue
            server[k] = s[k]

        # update weight here.
        val = server.get(search_item)
        if val and val == search_val:
            server['weight'] = args.weight

        servers.append(server)

    client.put_upstream(up_id=upstream.get('id'),
                        name=upstream.get('name'),
                        servers=servers)

    if not client.request_ok():
        print('update upstream weight failed: {}')
        exit(1)

    print('upstream id: {}, {}: "{}" update weight to "{}"'
          .format(upstream.get('id'), search_item, search_val, args.weight))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='update upstream weight')

    parser.add_argument('--upstream-ip',
                        dest='upstream_ip',
                        help='update the weight according to the upstream ip')
    parser.add_argument('--upstream-domain',
                        dest='upstream_domain',
                        help='update the weight according to the'
                        ' upstream domain')
    parser.add_argument('--weight',
                        dest='weight',
                        type=int,
                        required=True,
                        help='upstream weight')
    parser.add_argument('--upstream-id',
                        dest='upstream_id',
                        type=int,
                        help='select a upstream according to the upstream_id')

    args = parser.parse_args()

    main(args)
