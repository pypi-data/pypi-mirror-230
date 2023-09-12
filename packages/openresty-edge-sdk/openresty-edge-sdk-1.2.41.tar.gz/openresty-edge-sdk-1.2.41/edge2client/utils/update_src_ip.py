#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
update rule condition values.
"""

import json
import argparse
from utils_common import proc_cond, proc_conseq, \
        proc_waf, proc_proxy, proc_cache, proc_content

try:
    import py_client
except ImportError:
    print("Error: cannot import py_client.py")
    exit(1)


def update_cond(cond, vals, type):
    values = []

    for val in vals:
        values.append({'val': val, 'type': type})

    new_cond = cond.copy()
    new_cond['values'] = values
    return new_cond


def main(args):
    client = py_client.get_client()
    client.use_app(args.app_id)

    rule = client.get_rule(args.rule_id)
    rule_conds = rule.get('conditions')

    if rule_conds is None:
        print('>>> ERR: there\'s no conditions to modify in the rule \'{}\''
              .format(args.rule_id))
        exit(1)

    conds = []
    if len(rule_conds) == 1:
        rule_cond = rule_conds[0]
        conds.append(update_cond(rule_cond, args.ip, args.val_type))

    elif args.var_name:
        for rule_cond in rule_conds:
            if args.var_name == rule_cond.get('variable', {}).get('name'):
                conds.append(update_cond(rule_cond, args.ip, args.val_type))
            else:
                conds.append(rule_cond)

    if args.dry_run:
        print('old rule condtions:')
        print(json.dumps(rule_conds))
        print('new rule condtions:')
        print(json.dumps(conds))
        print('exiting...')
        exit(0)

    print('update rule conditions...')
    # update rule_conds.
    client.put_rule(
            rule_id=args.rule_id,
            condition=proc_cond(conds),
            conseq=proc_conseq(rule.get('actions')),
            waf=proc_waf(rule.get('waf')),
            cache=proc_cache(rule.get('cache')),
            proxy=proc_proxy(rule.get('proxy')),
            content=proc_content(rule.get('content')),
            top=rule.get('top'),
            last=rule.get('last'),
            order=rule.get('order')
        )
    print('done.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='update rule\'s condition value.')

    parser.add_argument('--dry-run',
                        dest='dry_run',
                        action='store_true',
                        help='dry run.')

    parser.add_argument('--app-id', type=int, dest='app_id',
                        help='Application id', required=True)
    parser.add_argument('--rule-id', type=int, dest='rule_id',
                        help='Rule id', required=True)

    parser.add_argument('--var-name', type=str, dest='var_name',
                        help='Specify a vairable name to '
                        'select among multiple condtions: '
                        '[client-addr first-x-forwarded-addr '
                        'last-x-forwarded-addr]')
    parser.add_argument('--val-type', type=str, dest='val_type',
                        help='Value type: [str rx wc netaddr]',
                        default='netaddr')
    parser.add_argument('--print-rules', dest='print_rules',
                        help=argparse.SUPPRESS, action='store_true')

    parser.add_argument('ip', metavar='IP', type=str, nargs='+',
                        help='set condition ip.')

    args = parser.parse_args()

    main(args)
