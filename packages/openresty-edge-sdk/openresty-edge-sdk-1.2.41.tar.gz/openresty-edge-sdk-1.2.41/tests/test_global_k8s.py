# -*- coding: utf-8 -*-
# import io
import sdk_test


class TestGlobalK8S(sdk_test.TestSdk):
    def test_global_k8s(self):
        client = self.client

        k8s_id = client.new_global_k8s(name = "k8s_sdk_test", host = "120.24.93.4",
            port = 9443, token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Im9wZW5yZXN0eS1lZGdlLXd5LXRva2VuLTg1YjVkIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6Im9wZW5yZXN0eS1lZGdlLXd5Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiZGRkZjRmODItODcyZi00ODRiLWI1ZTgtYjEwMWZjYzI5ODcxIiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OmRlZmF1bHQ6b3BlbnJlc3R5LWVkZ2Utd3kifQ.WldqXAWALlSJlo9lY6wsES4iE-BJcEnDSK_YD4M2xMx8qYvrzCdzjcRX6Dl56tR1Yv98QutEcyG_hjfjdYt_pDI_pgni3f4-jEjXrSDOiPw7kXschhaqVaN1mDEOGuOi2mtGtfEz6tPg-j4dbUuvmR3S5niBAh9tbe9_IacRiEt9HEYw0W-knoHyrOofHUY99JCnVjtXADhfLMQQyo0Ok8FNEjb06qMWVF_vwy6CJKWZy6dmVX1SXT494rToy97dEvfHtMqSxQOnCEKZ-8XwxgUTBPExpbX52tyJ8D2xmIorQVnJovCL2anwLMieYkD5F11KtFDozI510AyXR2i9FA", ssl_verify = False)

        self.assertIs(type(k8s_id), int)
        self.assertGreater(k8s_id, 0)
        self.global_k8s_id = k8s_id

        data = client.get_global_k8s(k8s_id)

        self.assertEqual(data["name"], "k8s_sdk_test")
        self.assertEqual(data["host"], "120.24.93.4")
        self.assertEqual(data["port"], 9443)
        self.assertEqual(data["id"], k8s_id)
        self.assertEqual(data["ssl_verify"], False)

        all_k8s = client.get_all_global_k8s()

        self.assertEqual(len(all_k8s), 1)

        self.assertEqual(all_k8s[0]["id"], k8s_id)

        # no k8s enviroment in ci
        k8s_detail = client.get_k8s_services_detail(k8s_id)
        self.assertNotEqual(k8s_detail, None)

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
                'ip' : '172.20.2.139',
                'port' : 80,
                'weight' : 3,
            }
        ]

        upstream_id = client.new_global_k8s_upstream(name = 'test_global_k8s_sdk', k8s_services = k8s_services, nodes = nodes)

        # no k8s environment in ci
        res = client.put_global_k8s_upstream(up_id = upstream_id, name = "test_global_k8s_sdk2", k8s_services = k8s_services)
        self.assertEqual(res, True)

        res = client.get_global_k8s_upstream(upstream_id)
        self.assertEqual(res['k8s_services'][0]['k8s'], k8s_id)
        self.assertEqual(res['k8s_services'][0]['k8s_namespace'], 'default')
        self.assertEqual(res['k8s_services'][0]['k8s_service'], 'test-hello')
        self.assertEqual(res['k8s_services'][0]['k8s_service_port'], 80)

        res = client.get_all_global_k8s_upstreams()
        self.assertEqual(len(res), 1)

        res = client.del_global_k8s_upstream(upstream_id)
        self.assertEqual(res, True)
