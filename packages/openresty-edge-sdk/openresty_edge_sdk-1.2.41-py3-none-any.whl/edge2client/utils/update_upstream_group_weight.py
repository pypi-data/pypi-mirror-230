#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
update app's upstream weight
"""

import argparse
import re
from math import gcd, ceil

try:
    import py_client
except ImportError:
    print("Error: cannot import py_client.py")
    exit(1)


def group_weight_parser(string):
    arr = string.split(':')

    if len(arr) != 2:
        msg = 'should be <group>:<weight> format but "%r" found' % string
        raise argparse.ArgumentTypeError(msg)

    return arr


def upstream_name_parser(s):
    result = re.match('(.*)-([^-]+)$', s)

    if result is None:
        msg = '%r is not well formed upstream_name' % s
        print(msg)
        exit(1)

    return result


def conv_proxy(old_proxy, new_upstreams):
    return {
        'upstreams': new_upstreams,
    }


def find_upstream_by_id(up_id, upstreams):
    for up in upstreams:
        if up_id == up.get('cluster'):
            return True

    return False


def parse_group_weight_dict(group_weight):
    group_weight_dict = {}

    weight_gcd = None
    last_weight = None
    for gw in group_weight:
        group = gw[0]
        weight = int(gw[1])
        group_weight_dict[group] = weight
        if weight_gcd is None:
            weight_gcd = weight
        if last_weight is not None:
            weight_gcd = gcd(weight, weight_gcd)
        last_weight = weight

    max_weight = 0

    for group in group_weight_dict.keys():
        if weight_gcd > 0:
            new_weight = int(group_weight_dict[group] / weight_gcd)
            group_weight_dict[group] = new_weight

            if new_weight > max_weight:
                max_weight = new_weight

    if max_weight > 20:
        roughly_scale = ceil(max_weight / 20)

        for group in group_weight_dict.keys():
            new_weight = ceil(group_weight_dict[group] / roughly_scale)

            if new_weight < 0:
                new_weight = 0
            elif new_weight > 20:
                new_weight = 20

            group_weight_dict[group] = new_weight

    return group_weight_dict


def get_proxy_rules(client):
    rules = client.get_all_rules()

    proxy_rules = []

    for rule in rules:
        if rule.get('proxy'):
            old_rule = rule

            proxy_rule = {}
            for k in old_rule.keys():
                if k.startswith('_'):
                    continue
                proxy_rule[k] = old_rule[k]

            proxy_rules.append(proxy_rule)

    return proxy_rules


def modify_proxy_rule(client, args, proxy_rule,
                      group_weight_dict, all_upstreams):
    proxy_rule_id = proxy_rule.get('id')

    upstreams = []
    old_proxy = proxy_rule.get('proxy')
    if not old_proxy:
        print('there is no proxy rules.')
        exit(1)

    id_weight_dict = {}
    for up in old_proxy.get('upstream', []):
        up_id = up.get('cluster')
        upstream = client.get_upstream(up_id)
        id_weight_dict[up_id] = up.get('weight', 0)
        upstreams.append(upstream)

    new_upstreams = []
    serv_names = []
    unchanged_weight_cnt = 0

    for up in upstreams:
        up_name = up.get('name')
        up_group = up.get('group')

        if up_group is None or up_group == '':
            print('>>> WARN: upstream "{}" does not have a group name.'
                  .format(up_name), flush=True)
            up_id = up.get('id')
            weight = id_weight_dict.get(up_id, 0)

            print('id: {}, upstream_name: {}, weight: {}'
                  .format(up_id, up_name, weight),
                  flush=True)

            unchanged_weight_cnt += 1
            new_upstreams.append({'upstream': up_id, 'weight': weight})
            continue

        ret = upstream_name_parser(up_name)
        serv_name = ret.group(1)
        group_name = ret.group(2)

        if up_group != group_name:
            print('"{}" (group: {}) is not a well-formed upstream_name'
                  .format(up_name, up_group))
            exit(1)

        if serv_name not in serv_names:
            serv_names.append(serv_name)

    for grp in group_weight_dict.keys():
        weight = group_weight_dict.get(grp)
        if weight is None:
            continue

        for serv_name in serv_names:
            up_name = '{}-{}'.format(serv_name, grp)
            up_id = all_upstreams.get(up_name)
            old_weight = id_weight_dict.get(up_id, 0)
            if not up_id:
                print('>>> WARN: group: {}, upstream_name: {} does not exists.'
                      .format(grp, up_name), flush=True)
                continue

            if old_weight == weight:
                unchanged_weight_cnt += 1
            print('id: {}, upstream_name: {}, group: {}, weight: {} -> {}'
                  .format(up_id, serv_name, grp, old_weight, weight),
                  flush=True)

            if find_upstream_by_id(up_id, old_proxy.get('upstream', [])):
                new_upstreams.append({'upstream': up_id, 'weight': weight})
                continue

            # found which group
            for tmp_grp in group_weight_dict.keys():
                tmp_up_id = all_upstreams.get('{}-{}'
                                              .format(serv_name, tmp_grp))
                if find_upstream_by_id(tmp_up_id, old_proxy.get('upstream')):
                    new_upstreams.append({'upstream': up_id, 'weight': weight})
                    break

    # diff upstream
    for up in upstreams:
        up_id = up.get('id')
        found = False

        for nup in new_upstreams:
            if up_id == nup.get('upstream'):
                found = True
                break

        if not found:
            weight = id_weight_dict.get(up_id, 0)

            print('id: {}, upstream_name: {}, weight: {}'
                  .format(up_id, up.get('name'), weight),
                  flush=True)

            unchanged_weight_cnt += 1
            new_upstreams.append({'upstream': up_id, 'weight': weight})

    weight_zero_cnt = 0
    # check new_upstreams before send
    for nup in new_upstreams:
        if nup.get('weight') == 0:
            weight_zero_cnt += 1

    if weight_zero_cnt == len(new_upstreams):
        print('!!!ERROR: all upstream weight is zero, '
              'exiting...')
        exit(1)

    new_proxy = conv_proxy(old_proxy, new_upstreams)

    if len(new_upstreams) == unchanged_weight_cnt:
        print('nothing changed in this rule, skip...')
        return

    if args.dry_run:
        print('dry run here. exiting...')
        return

    ok = client.patch_rule(proxy_rule_id, proxy=new_proxy)
    if ok:
        print('modified upstream group weight successfully.', flush=True)
    else:
        print('something wrong happend.', flush=True)


def main(args):
    # init
    client = py_client.get_client()
    client.use_app(args.app_id)

    group_weight_dict = parse_group_weight_dict(args.group_weight)

    proxy_rules = get_proxy_rules(client)
    all_upstreams = client.get_all_upstreams()

    for proxy_rule in proxy_rules:
        print("{} rule_id: {} {}"
              .format('-' * 10, proxy_rule.get('id'), '-' * 10), flush=True)
        modify_proxy_rule(client, args, proxy_rule,
                          group_weight_dict, all_upstreams)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='update upstream group weight')

    parser.add_argument('--dry-run',
                        dest='dry_run',
                        action='store_true',
                        help='dry run.')
    parser.add_argument('--app-id',
                        dest='app_id',
                        type=int,
                        required=True,
                        help='specifiy the app_id to operate on.')
    parser.add_argument('--group-weight',
                        dest='group_weight',
                        type=group_weight_parser,
                        required=True,
                        nargs='+',
                        help='upstream group:weight')

    args = parser.parse_args()

    main(args)
