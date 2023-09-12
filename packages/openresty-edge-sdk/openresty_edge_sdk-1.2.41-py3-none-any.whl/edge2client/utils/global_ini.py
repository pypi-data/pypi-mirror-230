#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import configparser

try:
    import py_client
except ImportError:
    print("Error: cannot import py_client.py")
    exit(1)

GLOBAL_VARS = []
HTML_FILES = {
    'html/50x.html': """
<!DOCTYPE html>
<html>
<head>
<title>Error</title>
<style>
    body {
        width: 35em;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
    }
</style>
</head>
<body>
<h1>An error occurred.</h1>
<p>Sorry, the page you are looking for is currently unavailable.<br/>
Please try again later.</p>
<p>If you are the system administrator of this resource then you should check
the <a href="http://nginx.org/r/error_log">error log</a> for details.</p>
<p><em>Faithfully yours, OpenResty.</em></p>
</body>
</html>
"""
}
CLUSTER_GROUPS = []


def add_global_ngx_conf(client):
    config = {
        'ignore_invalid_headers': True,
        'ssl_session_ttl': 5,
        'ssl_session_ttl_unit': 'min',
        'ssl_protocols': [
            'SSLv3',
            'TLSv1',
            'TLSv1.1',
            'TLSv1.2'],
        'ssl_ciphers': 'EECDH+CHACHA20:EECDH+CHACHA20-draft:EECDH+AES128'
                       ':RSA+AES128:EECDH+AES256:RSA+AES256:EECDH+3DES'
                       ':RSA+3DES:!MD5',
        'ssl_prefer_server_ciphers': True}

    ok = client.set_global_ngx_config(config)
    if not ok:
        print('ERROR: set global nginx configures failed.')


def add_upstream_ngx_conf(client, conf_obj):
    if not conf_obj.has_section('upstream'):
        conf_obj.add_section('upstream')

    upstreams = client.get_all_global_upstreams()
    upstream_names = []
    for upstream in upstreams:
        upstream_names.append(upstream.get('name'))
        conf_obj.set('upstream', str(upstream.get('name')),
                     str(upstream.get('id')))


def add_variables_ngx_conf(client, conf_obj):
    if not conf_obj.has_section('variable'):
        conf_obj.add_section('variable')

    variables = client.get_all_global_vars()
    variable_names = {}

    for variable in variables:
        variable_names[variable.get('name')] = variable.get('id')

        conf_obj.set('variable',
                     str(variable.get('name')),
                     str(variable.get('id')))

    for var in GLOBAL_VARS:
        if var.get('name') not in variable_names:
            print('adding global variables ...')
            var_id = client.new_global_var(**var)
            conf_obj.set('variable', str(var.get('name')), str(var_id))


def add_actions_ngx_conf(client, conf_obj):
    if not conf_obj.has_section('action'):
        conf_obj.add_section('action')

    actions = client.get_all_global_actions()
    action_names = []

    for action in actions:
        action_names.append(action.get('name'))
        conf_obj.set('action', str(action.get('name')), str(action.get('id')))

    if 'default_set_proxy_header' not in action_names:
        print('adding global action default_set_proxy_header...')
        action_name = 'default_set_proxy_header'
        conseq = [
            {'set-proxy-header': {
                'header': 'X-Real-Scheme', 'el_var': 'scheme'}},
            {'set-proxy-header': {'header': 'Host', 'el_var': 'host'}},
            {'set-proxy-header': {
                'header': 'X-Real-IP', 'el_var': 'client-addr'}},
            {'append-proxy-header-value': {'header': 'X-Forwarded-For',
                                           'el_var': 'client-addr'}}
        ]
        action_id = \
            client.new_global_action(name=action_name, conseq=conseq)
        conf_obj.set('action', 'default_set_proxy_header', str(action_id))


def add_static_file_ngx_conf(client, conf_obj):
    static_files = client.get_all_static_files()
    static_files_labels = {}

    for static_file in static_files:
        label = static_file.get('label')
        if label:
            static_files_labels[label] = static_file.get('id')

    if not conf_obj.has_section('favicon'):
        conf_obj.add_section('favicon')

    if not conf_obj.has_section('html'):
        conf_obj.add_section('html')

    for html_label, html_content in HTML_FILES.items():
        if html_label not in static_files_labels:
            print('adding html static files ...')
            file_id = client.upload_static_file(
                label=html_label, content=html_content)
            conf_obj.set('html', str(html_label), str(file_id))
        else:
            conf_obj.set('html', str(html_label),
                         str(static_files_labels[html_label]))


def add_ssl_ngx_conf(client, conf_obj):
    if not conf_obj.has_section('ssl_cert'):
        conf_obj.add_section('ssl_cert')

    global_certs = client.get_all_global_cert_key()
    print(global_certs)
    cert_labels = {}

    for cert in global_certs:
        if cert.get('label'):
            cert_labels[cert.get('label')] = cert.get('id')


def add_cluster_ngx_conf(client, conf_obj):
    if not conf_obj.has_section('cluster'):
        conf_obj.add_section('cluster')

    all_cluster_groups = client.get_all_cluster_groups()
    cluster_names = {}
    for cluster_group in all_cluster_groups:
        if cluster_group.get('name') and cluster_group.get('id'):
            cluster_names[cluster_group.get('name')] \
                = cluster_group.get('id')

            conf_obj.set('cluster',
                         str(cluster_group.get('name')),
                         str(cluster_group.get('id')))

    for cluster_name in CLUSTER_GROUPS:
        if cluster_name not in cluster_names:
            print('adding cluster group ...')
            cluster_id = client.new_cluster_group(cluster_name)
            conf_obj.set('cluster', str(cluster_name), str(cluster_id))


def main():
    client = py_client.get_client()
    if not client:
        exit(1)

    conf_obj = configparser.ConfigParser()

    print('adding global nginx configures...')
    add_global_ngx_conf(client)

    cwd = os.getcwd()
    global_config_file_path = os.path.join(cwd, "global.ini")

    # read old global configures
    if os.path.isfile(global_config_file_path):
        conf_obj.read(global_config_file_path, encoding="utf-8")

    print('adding upstream nginx configures...')
    add_upstream_ngx_conf(client, conf_obj)

    print('adding variables nginx configures...')
    add_variables_ngx_conf(client, conf_obj)

    print('adding actions nginx configures...')
    add_actions_ngx_conf(client, conf_obj)

    print('adding static file nginx configures...')
    add_static_file_ngx_conf(client, conf_obj)

    print('adding ssl nginx configures...')
    add_ssl_ngx_conf(client, conf_obj)

    print('adding cluster nginx configures...')
    add_cluster_ngx_conf(client, conf_obj)

    print('writing config.ini...: ' + global_config_file_path)
    with open(global_config_file_path, 'w') as cf_file:
        conf_obj.write(cf_file)

    print('all done')


if __name__ == '__main__':
    main()
