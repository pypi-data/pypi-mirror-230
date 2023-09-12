#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
This file is used to export csv from api
"""

try:
    import py_client
except ImportError:
    print("Error: cannot import py_client.py")
    exit(1)


def main():
    client = py_client.get_client()
    data = client.get_all_apps(detail=True)

    cached_partitions = {}

    print("domain,port,partition,label")
    for info in data.values():
        csv_table = {
            'domain': [],
            'port': [],
            'partition': [],
            'label': None
        }
        csv_table['label'] = info['label']
        for domain in info['domains']:
            csv_table['domain'].append(domain['domain'])
        if info['http_ports']:
            for port in info['http_ports']:
                csv_table['port'].append(str(port))
        if info['https_ports']:
            for port in info['https_ports']:
                csv_table['port'].append(str(port))
        for partition in info['partitions']:
            if partition in cached_partitions:
                pass
            else:
                partition_data = client.get_cluster_group(partition)
                cached_partitions[partition] = partition_data['name']

            csv_table['partition'].append(cached_partitions[partition])
            print(u"{},{},{},{}".format(
                "|".join(csv_table['domain']),
                "|".join(csv_table['port']),
                "|".join(csv_table['partition']),
                csv_table['label']
            ))


if __name__ == '__main__':
    main()
