#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
copy application rules.
"""

import argparse
from utils_common import proc_cond, proc_conseq, \
        proc_waf, proc_proxy, proc_cache, proc_content

try:
    import json
except ImportError:
    print('>>> WARN: cannot import json')

try:
    import py_client
except ImportError:
    print("Error: cannot import py_client.py")
    exit(1)


def clone_upstream(proxy, client, src_id, dst_id):
    dst_proxy = {
        'connect_timeout': proxy.get('connect_timeout'),
        'read_timeout': proxy.get('read_timeout'),
        'send_timeout': proxy.get('send_timeout'),
        'retries': proxy.get('retries'),
        'retry_condition': proxy.get('retry_condition'),
        'multi_tier': proxy.get('layer_policty'),
        'balancer_algorithm': proxy.get('balancer', {}).get('algorithm'),
        'balancer_vars': proxy.get('balancer', {}).get('variables'),
    }

    for field in ['upstream', 'backup_upstream']:
        dst_upstreams = []
        for upstream in proxy.get(field, []):
            client.use_app(src_id)
            upobj = client.get_upstream(upstream.get('cluster'))

            client.use_app(dst_id)
            servers = []
            for node in upobj.get('nodes'):
                servers.append({
                    'domain': node.get('domain'),
                    'ip': node.get('ip'),
                    'port': node.get('port'),
                    'weight': node.get('weight'),
                    'status': node.get('status')
                })
            health_checker = {}
            checker = upobj.get('checker')
            if checker and upobj.get('enable_checker'):
                for k in ['use_tcp', 'fall', 'http_req_host',
                          'http_req_uri', 'interval', 'interval_unit',
                          'report_interval', 'report_interval_unit',
                          'rise', 'timeout', 'valid_statuses',
                          'user_agent', 'http_ver']:
                    if checker.get(k) is not None:
                        health_checker[k] = checker.get(k)

            # XX: reuse upstream here
            upstreams = client.get_all_upstreams()

            if upstreams.get(upobj.get('name')):
                cluster_id = upstreams.get(upobj.get('name'))

            else:
                cluster_id = client.new_upstream(
                    name=upobj.get('name'),
                    servers=servers,
                    health_checker=health_checker,
                    ssl=upobj.get('ssl'),
                    group=upobj.get('group')
                )

            dst_upstreams.append({
                'cluster': cluster_id,
                'global_cluster': upstream.get('global_cluster', None),
                'weight': upstream.get('weight')
            })

        # update proxy upstream id
        if dst_upstreams:
            dst_proxy[field] = dst_upstreams

    return dst_proxy


def main(args):
    src_id, dst_id = args.from_id, args.to_id

    # src
    client = py_client.get_client()
    client.use_app(src_id)

    # app rules
    src_rules = client.get_all_rules()

    # check dst rules
    client.use_app(dst_id)
    dst_rules = client.get_all_rules()
    if len(dst_rules) > 0:
        print('>>> WARN: dst application already has rules. ')

        if not args.force:
            print('>>> ERR: please use --force option to overwrite the rules. '
                  'exiting...')
            exit(1)

        print('>>> WARN: overwriting the rules...')
        # clear the dst rules.
        for rule in dst_rules:
            client.del_rule(rule.get('id'))
        # clear the upstreams.
        all_upstreams = client.get_all_upstreams()
        for up_name in all_upstreams:
            client.del_upstream(all_upstreams[up_name])

    for rule in src_rules:
        if rule.get('actions') is None \
                and rule.get('waf') is None \
                and rule.get('cache') is None \
                and rule.get('content') is None \
                and rule.get('proxy') is None:
            continue

        proxy = rule.get('proxy')
        dst_proxy = None
        if proxy:
            dst_proxy = clone_upstream(proxy, client, src_id, dst_id)
            client.use_app(dst_id)

        client.new_rule(
                condition=proc_cond(rule.get('conditions', None)),
                conseq=proc_conseq(rule.get('actions')),
                waf=proc_waf(rule.get('waf')),
                cache=proc_cache(rule.get('cache')),
                proxy=proc_proxy(dst_proxy),
                content=proc_content(rule.get('content')),
                top=rule.get('top'),
                last=rule.get('last'),
                order=rule.get('order')
            )

    # check missing upstreams here
    client.use_app(src_id)
    src_upstreams = client.get_all_upstreams()

    client.use_app(dst_id)
    dst_upstreams = client.get_all_upstreams()

    for sup_name in src_upstreams:
        if dst_upstreams.get(sup_name):
            pass
        else:
            client.use_app(src_id)
            upobj = client.get_upstream(src_upstreams.get(sup_name))

            servers = []
            for node in upobj.get('nodes'):
                servers.append({
                    'domain': node.get('domain'),
                    'ip': node.get('ip'),
                    'port': node.get('port'),
                    'weight': node.get('weight'),
                    'status': node.get('status')
                })

            health_checker = {}
            checker = upobj.get('checker')
            if checker and upobj.get('enable_checker'):
                for k in ['use_tcp', 'fall', 'http_req_host',
                          'http_req_uri', 'interval', 'interval_unit',
                          'report_interval', 'report_interval_unit',
                          'rise', 'timeout', 'valid_statuses',
                          'user_agent', 'http_ver']:
                    if checker.get(k) is not None:
                        health_checker[k] = checker.get(k)

            client.use_app(dst_id)
            client.new_upstream(
                name=upobj.get('name'),
                servers=servers,
                health_checker=health_checker,
                ssl=upobj.get('ssl'),
                group=upobj.get('group')
            )

    if args.print_rules:
        print(json.dumps(client.get_all_rules()))

    # whitelist
    client.use_app(src_id)
    waf_whitelists = client.get_all_waf_whitelists()

    client.use_app(dst_id)
    for waf_whitelist in waf_whitelists:
        client.new_waf_whitelist(
            condition=proc_cond(waf_whitelist.get('conditions')),
            rule_sets=waf_whitelist.get('rule_sets'))

    if args.print_waf_whitelist:
        print(json.dumps(client.get_all_waf_whitelists()))

    # cert
    client.use_app(src_id)
    if client.get_all_cert_keys():
        print('>>> WARN: there are ssl certificate related configuration, '
              'please confirm.')


'''
    client.use_app(dst_id)

    if args.print_cert:
        print(json.dumps(client.get_all_cert_keys()))
'''


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='application copy')

    parser.add_argument('--dry-run',
                        dest='dry_run',
                        action='store_true',
                        help='dry run.')
    parser.add_argument('--force',
                        dest='force',
                        action='store_true',
                        help='overwrite the rules of dst application.')
    parser.add_argument('from_id', metavar='from-ID', type=int,
                        help='copy application from-ID')
    parser.add_argument('to_id', metavar='to-ID', type=int,
                        help='copy application to-ID')

    parser.add_argument('--print-rules', help=argparse.SUPPRESS,
                        dest='print_rules',
                        action='store_true')
    parser.add_argument('--print-waf-whitelist', help=argparse.SUPPRESS,
                        dest='print_waf_whitelist',
                        action='store_true')

    args = parser.parse_args()

    main(args)

'''
    parser.add_argument('--cert-key', type=str, dest='cert_key',
                        help='specify the certificate key file.')
    parser.add_argument('--print-cert',
                        dest='print_cert',
                        action='store_true')
'''
