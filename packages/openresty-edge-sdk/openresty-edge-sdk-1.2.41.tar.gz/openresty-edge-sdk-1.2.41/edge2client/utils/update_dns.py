#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""
update dns record
"""

import argparse
import sys
# import json


try:
    sys.path.append('/usr/local/oredge-python-sdk/lib')
    import py_client
except ImportError:
    print("Error: cannot import py_client.py")
    exit(1)


def parse_records(record):
    record_list = record.split(':', 1)
    if not record_list:
        raise argparse.ArgumentTypeError("failed to parse record")

    return record_list


def yes_or_no(question):
    reply = str(input(question+' (y/n): ')).lower().strip()
    if reply[0] == 'y':
        return True
    if reply[0] == 'n':
        return False
    else:
        return yes_or_no("Uhhhh... please enter ")


def main(args):
    client = py_client.get_client()

    dns_app = client.get_dns_app(args.dns_id)
    if not dns_app:
        raise Exception('DNS app not found:', args.dns_id)

    if not yes_or_no('dns zone: ' + dns_app.get('zone')):
        print("exiting ...")
        exit(0)

    client.use_dns_app(args.dns_id)

    args_records = {}
    for args_record in args.records:
        args_records[args_record[0]] = args_record[1]

    dns_records = client.get_dns_records()

    new_record_list = []
    update_record_list = []
    update_record_exists = {}

    # records to be update
    for dns_record in dns_records.get('data'):
        if dns_record.get('type') == 'A':
            sub_domain = dns_record.get('sub_domain')
            args_record_ip = args_records.get(sub_domain)

            if args_record_ip == dns_record.get('ip'):
                update_record_exists[sub_domain] = True

                print("info: skip update this record: ",
                      sub_domain, ":", args_record_ip)
                continue

            if args_record_ip:
                update_record_list.append({
                    'record_id': dns_record.get('id'),
                    'record_type': 'A',
                    'sub_domain': dns_record.get('sub_domain'),
                    'ip': args_record_ip
                })

                update_record_exists[sub_domain] = True

    for sub_domain, ip in args_records.items():
        if not update_record_exists.get(sub_domain):
            new_record_list.append({
                'record_type': 'A',
                'sub_domain': sub_domain,
                'ip': ip
            })

    for record in new_record_list:
        print("append new record: %s %s %s" % (record.get('sub_domain'),
              record.get('record_type'), record.get('ip')))

        if args.dry_run:
            print('dry run ...')
        else:
            client.new_dns_record(sub_domain=record.get('sub_domain'),
                                  record_type=record.get('record_type'),
                                  ip=record.get('ip'))

    for record in update_record_list:
        print("update record: %s %s %s" % (record.get('sub_domain'),
              record.get('record_type'), record.get('ip')))

        if args.dry_run:
            print('dry run ...')
        else:
            client.put_dns_record(sub_domain=record.get('sub_domain'),
                                  record_type=record.get('record_type'),
                                  ip=record.get('ip'),
                                  record_id=record.get('record_id'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='update dns A record')

    parser.add_argument('--dry-run',
                        dest='dry_run',
                        action='store_true',
                        help='dry run.')
    parser.add_argument('--dns-id',
                        dest='dns_id',
                        type=int,
                        required=True)
    parser.add_argument('records', metavar='SUB_DOMAIN:IP', nargs='+',
                        type=parse_records, help='dns records')
    args = parser.parse_args()

    main(args)
