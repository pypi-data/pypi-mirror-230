# -*- coding: utf-8 -*-
# import io
import sdk_test


class TestK8sUpstream(sdk_test.TestSdk):
    def test_k8s_upstream(self):
        client = self.client
        k8s_id = client.new_global_k8s(name = "k8s_sdk_test", host = "192.168.122.220",
            port = 9443, token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Im9wZW5yZXN0eS1lZGdlLXd5LXRva2VuLTg1YjVkIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6Im9wZW5yZXN0eS1lZGdlLXd5Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiZGRkZjRmODItODcyZi00ODRiLWI1ZTgtYjEwMWZjYzI5ODcxIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OmRlZmF1bHQ6b3BlbnJlc3R5LWVkZ2Utd3kifQ.WldqXAWALlSJlo9lY6wsES4iE-BJcEnDSK_YD4M2xMx8qYvrzCdzjcRX6Dl56tR1Yv98QutEcyG_hjfjdYt_pDI_pgni3f4-jEjXrSDOiPw7kXschhaqVaN1mDEOGuOi2mtGtfEz6tPg-j4dbUuvmR3S5niBAh9tbe9_IacRiEt9HEYw0W-knoHyrOofHUY99JCnVjtXADhfLMQQyo0Ok8FNEjb06qMWVF_vwy6CJKWZy6dmVX1SXT494rToy97dEvfHtMqSxQOnCEKZ-8XwxgUTBPExpbX52tyJ8D2xmIorQVnJovCL2anwLMieYkD5F11KtFDozI510AyXR2i9FA", ssl_verify = False)

        self.assertIs(type(k8s_id), int)
        self.assertGreater(k8s_id, 0)
        self.global_k8s_id = k8s_id

        k8s_services = [
            {
                'k8s' : k8s_id,
                'k8s_namespace' : 'default',
                'k8s_service' : 'test-hello',
                'k8s_service_port' : 80,
            }
        ]

        nodes = [
            {
                'ip' : "172.20.2.139",
                'port' : 80,
                'weight' : 3,
            }
        ]

        upstream_id = client.new_k8s_upstream(name = 'test_k8s_sdk', k8s_services = k8s_services, nodes = nodes)

        # no k8s environment in ci
        res = client.put_k8s_upstream(up_id = upstream_id, name = "test_k8s_sdk2", k8s_services = k8s_services)
        self.assertEqual(res, True)

        res = client.get_k8s_upstream(upstream_id)
        self.assertEqual(res['k8s_services'][0]['k8s'], k8s_id)
        self.assertEqual(res['k8s_services'][0]['k8s_namespace'], 'default')
        self.assertEqual(res['k8s_services'][0]['k8s_service'], 'test-hello')
        self.assertEqual(res['k8s_services'][0]['k8s_service_port'], 80)

        res = client.get_all_k8s_upstreams()
        self.assertEqual(len(res), 1)


        normal_up_id = client.new_upstream(
            name='origin-upstream',
            servers=[
                {'ip': '172.22.31.1', 'port': 80},
                {'ip': '172.22.31.2', 'port': 80, 'weight': 2}
            ])

        normal_upstream = client.get_upstream(normal_up_id)

        proxy_rule = {
            'upstreams': [{'k8s_upstream': upstream_id, 'weight': 1}, {'upstream': normal_up_id}],
            'retries': 2,
            'retry_condition' : ["invalid_header", "http_500"],
            'balancer_algorithm' : "roundrobin",
        }

        rule_id = client.new_rule(proxy = proxy_rule)
        self.assertNotEqual(rule_id, None)

        copy_up_id = client.copy_upstream_to_k8s_upstream(normal_up_id, k8s_services=k8s_services)

        self.assertIs(type(copy_up_id), int)

        copy_upstream = client.get_k8s_upstream(copy_up_id)


        self.assertEqual(copy_upstream.get('name'), normal_upstream.get('name'))
        self.assertEqual(copy_upstream.get('ssl'), normal_upstream.get('ssl'))
        self.assertEqual(copy_upstream.get('disable_ssl_verify'), normal_upstream.get('disable_ssl_verify'))
        self.assertEqual(copy_upstream.get('enable_checker'), normal_upstream.get('enable_checker'))

        res = client.get_rule(rule_id)

        proxy = res.get('proxy')
        self.assertNotEqual(proxy, None)

        upstreams = proxy.get('upstream')
        self.assertNotEqual(upstreams, None)

        for up in upstreams:
            k8s_cluster = up.get('k8s_cluster')
            self.assertNotEqual(k8s_cluster, None)

        res = client.del_rule(rule_id)
        self.assertEqual(res, True)

        res = client.del_k8s_upstream(copy_up_id)
        self.assertEqual(res, True)

        res = client.del_k8s_upstream(upstream_id)
        self.assertEqual(res, True)

    def test_search_k8s_upstream(self):
        client = self.client

        k8s_id = client.new_global_k8s(name = "k8s_sdk_test", host = "120.24.93.4",
            port = 9443, token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Im9wZW5yZXN0eS1lZGdlLXd5LXRva2VuLTg1YjVkIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6Im9wZW5yZXN0eS1lZGdlLXd5Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiZGRkZjRmODItODcyZi00ODRiLWI1ZTgtYjEwMWZjYzI5ODcxIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OmRlZmF1bHQ6b3BlbnJlc3R5LWVkZ2Utd3kifQ.WldqXAWALlSJlo9lY6wsES4iE-BJcEnDSK_YD4M2xMx8qYvrzCdzjcRX6Dl56tR1Yv98QutEcyG_hjfjdYt_pDI_pgni3f4-jEjXrSDOiPw7kXschhaqVaN1mDEOGuOi2mtGtfEz6tPg-j4dbUuvmR3S5niBAh9tbe9_IacRiEt9HEYw0W-knoHyrOofHUY99JCnVjtXADhfLMQQyo0Ok8FNEjb06qMWVF_vwy6CJKWZy6dmVX1SXT494rToy97dEvfHtMqSxQOnCEKZ-8XwxgUTBPExpbX52tyJ8D2xmIorQVnJovCL2anwLMieYkD5F11KtFDozI510AyXR2i9FA", ssl_verify = False)

        self.assertIs(type(k8s_id), int)
        self.assertGreater(k8s_id, 0)
        self.global_k8s_id = k8s_id

        k8s_services = [
            {
                'k8s' : k8s_id,
                'k8s_namespace' : 'default',
                'k8s_service' : 'test-hello',
                'k8s_service_port' : 80,
            }
        ]

        k8s_up_id = self.client.new_k8s_upstream(name = 'test_search_k8s_upstream1', k8s_services = k8s_services)
        k8s_global_up_id = self.client.new_global_k8s_upstream(name = 'test_search_k8s_upstream2', k8s_services = k8s_services)

        up_id = self.client.new_upstream(
            name='test_search_k8s_upstream3',
            servers=[
                {'ip': '172.22.31.1', 'port': 80},
                {'ip': '172.22.31.2', 'port': 80, 'weight': 2}
            ])

        global_up_id = self.client.new_global_upstream(
            name = 'test_search_k8s_upstream4',
            servers=[
                {'ip': '172.22.31.1', 'port': 80},
                {'ip': '172.22.31.2', 'port': 80, 'weight': 2}
            ])


        data = self.client.search_k8s_upstream_by_name("k8s_upstream")
        self.assertEqual(len(data), 2)

        for d in data:
            if d['name'] == "test_search_k8s_upstream1":
                self.assertEqual(d['upstream_type'], "k8s_http")
            elif d['name'] == "test_search_k8s_upstream2":
                self.assertEqual(d['upstream_type'], "k8s_global")
            else:
                raise Exception("search wrong k8s upstream")

        data = self.client.search_upstream_by_name("k8s_upstream")
        self.assertEqual(len(data), 2)

        for d in data:
            if d['name'] == "test_search_k8s_upstream3":
                self.assertEqual(d['upstream_type'], "http")
            elif d['name'] == "test_search_k8s_upstream4":
                self.assertEqual(d['upstream_type'], "global")
            else:
                raise Exception("search wrong not k8s upstream")

        data = self.client.search_k8s_upstream(namespace = "default", type_list=["k8s_global"])

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'test_search_k8s_upstream2')

        app_id = self.client.get_app_id()

        data = self.client.search_k8s_upstream(namespace = "default", type_list=["k8s_http"])

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'test_search_k8s_upstream1')
        self.assertEqual(data[0]['id'], k8s_up_id)
        self.assertEqual(data[0]['app_id'], app_id)

        data = self.client.search_k8s_upstream(service = "test-hello", type_list=["k8s_http"])

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'test_search_k8s_upstream1')
        self.assertEqual(data[0]['id'], k8s_up_id)
        self.assertEqual(data[0]['app_id'], app_id)

        data = self.client.search_k8s_upstream(port = 80, type_list=["k8s_http"])

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'test_search_k8s_upstream1')
        self.assertEqual(data[0]['id'], k8s_up_id)
        self.assertEqual(data[0]['app_id'], app_id)

        data = self.client.search_k8s_upstream(port = 80, service = "test-hello", type_list=["k8s_http"])

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'test_search_k8s_upstream1')
        self.assertEqual(data[0]['id'], k8s_up_id)
        self.assertEqual(data[0]['app_id'], app_id)

        data = self.client.search_k8s_upstream(port = 80, service = "test-hello2", type_list=["k8s_http"])

        self.assertEqual(len(data), 0)

        data = self.client.search_k8s_upstream_history(page=1, pagesize=5)

        self.assertEqual(len(data), 5)

        data = self.client.get_k8s_upstream(k8s_up_id)
        self.assertNotEqual(data, None)

        ip = data['nodes'][0]['ip']

        data = self.client.search_k8s_upstream_by_ip(ip = ip)
        self.assertEqual(len(data), 2)

        self.client.del_k8s_upstream(k8s_up_id)
        self.client.del_global_k8s_upstream(k8s_global_up_id)
        self.client.del_upstream(up_id)
        self.client.del_global_upstream(global_up_id)
