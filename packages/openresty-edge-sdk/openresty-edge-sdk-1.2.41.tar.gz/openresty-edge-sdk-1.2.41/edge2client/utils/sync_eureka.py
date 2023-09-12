from urllib.parse import urlparse
import requests

#
# NOTICE: please edit these following configurations.
#

EUREKA_ADDR = 'http://127.0.0.1:18080/eureka/apps/'

# key: Edge application domain
# value: eureka app array.
EUREKA_APPS = {
    'test.com': ['eureka-app-name-1', 'eureka-app-name-2'],
    'test-2.com': ['eureka-app-name-3']
}

#
# end of configurations
#

try:
    import py_client
except ImportError:
    print("Error: cannot import py_client.py")
    exit(1)


def get_upstreams_from_eureka(app_name, domain):
    upstreams = {}
    ssl = False
    interval = 30
    http_req_uri = '/health'

    r = requests.get(EUREKA_ADDR + app_name,
                     headers={'Content-Type': 'application/json',
                              'Accept': 'application/json'},
                     timeout=10)
    # print(r.text)
    response = r.json()
    application = response['application']
    upstreams['name'] = application['name']
    instances = application['instance']
    upstreams['servers'] = []
    upstreams['health_checker'] = {
        'http_req_uri': http_req_uri,
        'http_req_host': domain,
        'interval': 30,
        'interval_unit': 'sec',
        'timeout': 3,
        'fall': 3,
        'rise': 2,
        'valid_statuses': [200, 302],
        'report_interval': 3,
        'report_interval_unit': 'min'
    }

    for instance in instances:
        server = {}
        server['ip'] = instance['ipAddr']
        port = instance['port']
        secure_port = instance['securePort']
        if port['@enabled'] == 'true':
            server['port'] = port['$']
        elif secure_port['@enabled'] == 'true':
            server['port'] = port['$']
            ssl = True
        interval = instance['leaseInfo']['renewalIntervalInSecs']
        http_req_uri = urlparse(instance['healthCheckUrl']).path
        upstreams['servers'].append(server)

    upstreams['ssl'] = ssl
    upstreams['health_checker']['interval'] = interval
    upstreams['health_checker']['http_req_uri'] = http_req_uri

    return upstreams


def main():
    print('begin to sync from eureka')

    client = py_client.get_client()

    for domain, apps in EUREKA_APPS.items():
        has_changes = False
        eureka_upstream_names = []

        print('sync the upstream of ' + domain)
        data = client.search_app(app_domain = domain)
        if not data:
            print("ERROR: can not found app: " + domain)
            continue

        app_id = data[0]['id']
        client.use_app(app_id)
        exist_upstreams = client.get_all_upstreams()
        # print(exist_upstreams)

        for eureka_app in apps:
            eureka_upstream = get_upstreams_from_eureka(eureka_app, domain)
            if not eureka_upstream:
                print("ERROR: can not found upstreams in eureka, app is: "
                      + eureka_app)
                continue
            # print(eureka_upstream)

            name = eureka_upstream['name']
            eureka_upstream_names.append(name)

            if name not in exist_upstreams:
                client.new_upstream(
                    name=name, servers=eureka_upstream['servers'],
                    health_checker=eureka_upstream['health_checker'],
                    ssl=eureka_upstream['ssl'])
                has_changes = True
                print('add new upstream, name: ' + name)

            else:
                data = client.get_upstream(exist_upstreams[name])
                # print(data)
                need_update = False

                if data['checker']['http_req_uri'] != \
                    eureka_upstream['health_checker']['http_req_uri'] \
                    or data['checker']['interval'] != \
                    eureka_upstream['health_checker']['interval'] \
                        or data['ssl'] != eureka_upstream['ssl']:
                    need_update = True

                nodes = data['nodes']
                nodes = sorted(nodes, key=lambda node: node['ip'])
                eureka_nodes = sorted(eureka_upstream['servers'],
                                      key=lambda node: node['ip'])
                if len(nodes) != len(eureka_nodes):
                    need_update = True

                nodes_len = len(nodes)
                for i in range(nodes_len):
                    if nodes[i]['ip'] != eureka_nodes[i]['ip'] \
                            or nodes[i]['port'] != eureka_nodes[i]['port']:
                        need_update = True
                        break

                if need_update:
                    client.put_upstream(
                        exist_upstreams[name], name=name,
                        servers=eureka_upstream['servers'],
                        health_checker=eureka_upstream['health_checker'],
                        ssl=eureka_upstream['ssl'])
                    has_changes = True
                    print('updated exist upstream, name: ' + name)

        # delete the upstream that not in the eureka.
        # for up_name, up_id in exist_upstreams.items():
        #     if up_name not in eureka_upstream_names:
        #         client.del_upstream(up_id)
        #         has_changes = True
        #         print('deleted upstream, name is ' + up_name)

        if has_changes:
            client.new_release()

    print('done')


if __name__ == "__main__":
    main()
