# -*- coding: utf-8 -*-
# import io
import sdk_test


class TestUpstream(sdk_test.TestSdk):
    def test_upstream_and_proxy(self):
        up_id = self.client.new_upstream(
            name='origin-upstream',
            servers=[
                {'domain': 'test.com', 'port': 80},
                {'ip': '172.22.31.2', 'port': 80, 'weight': 2}
            ])
        self.assertIs(type(up_id), int)
        self.assertGreater(up_id, 0)

        changes = self.client.pending_changes()
        self.assertEqual(changes, 1)

        ok = self.client.put_upstream(
            up_id, name='origin-upstream',
            servers=[
                {'domain': 'app.com', 'port': 8080},
                {'ip': '172.22.31.2', 'port': 8080, 'weight': 1}
            ],
            health_checker={
                'http_req_uri': '/status',
                'http_req_host': 'test.com',
                'interval': 3,
                'interval_unit': 'sec',
                'timeout': 1,
                'fall': 3,
                'rise': 2,
                'valid_statuses': [200, 302],
                'report_interval': 3,
                'report_interval_unit': 'min'
            }
        )
        self.assertTrue(ok)

        data = self.client.get_upstream(up_id)
        self.__assert_upstream(data, {
            'name': 'origin-upstream',
            'nodes': [
                {'domain': 'app.com', 'port': 8080, 'status': 1},
                {'ip': '172.22.31.2', 'weight': 1, 'status': 1}
            ],
            'checker': {'interval': 3, 'rise': 2, 'http_req_uri': '/status'}
        })

        upstreams = self.client.get_all_upstreams()
        self.assertTrue('origin-upstream' in upstreams.keys())
        self.assertIs(type(upstreams['origin-upstream']), int)

        changes = self.client.pending_changes()
        self.assertEqual(changes, 2)

        self.client.new_release()
        changes = self.client.pending_changes()
        self.assertEqual(changes, 0)

        backup_up_id = self.client.new_upstream(
            name='backup-upstream',
            servers=[
                {'ip': '172.22.31.3', 'port': 80},
                {'ip': '172.22.31.4', 'port': 80, 'weight': 3}
            ])
        self.assertIs(type(backup_up_id), int)
        self.assertGreater(backup_up_id, up_id)

        proxy_rule = {
            'upstreams': [],
            'backup_upstreams': [],
            'upstream_el_code': 'true => set-upstream-addr(ip: "127.0.0.1", port: 80);',
            'retries': 2,
            "retry_condition": ["invalid_header", "http_500"],
            "balancer_algorithm": "hash",
            "balancer_vars": [
                {"name": "uri"},
                {
                    "name": "uri-arg",
                    "args": "foo"
                }
            ]
        }

        rule_id = self.client.new_rule(proxy=proxy_rule, top=1)
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        data = self.client.get_rule(rule_id)
        self.__assert_proxy_rule(data, {
            'proxy': {
                'upstream_el_code': 'true => set-upstream-addr(ip: "127.0.0.1", port: 80);',
                'retries': 2,
                'retry_condition': ['invalid_header', 'http_500'],
                'balancer': {
                    'algorithm': 'hash',
                    'variables': [
                        {'name': 'uri'},
                        {'name': 'uri-arg', 'args': 'foo'}
                    ]
                }
            }
        })


        proxy_rule = {
            'upstreams': [{'upstream': up_id, 'weight': 2}],
            'backup_upstreams': [{'upstream': backup_up_id}],
            'retries': 2,
            "retry_condition": ["invalid_header", "http_500"],
            "balancer_algorithm": "hash",
            "balancer_vars": [
                {"name": "uri"},
                {
                    "name": "uri-arg",
                    "args": "foo"
                }
            ]
        }
        ok = self.client.put_rule(rule_id=rule_id, proxy=proxy_rule)
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        proxy_rule['upstreams'][0]['weight'] = 3
        ok = self.client.put_rule(rule_id=rule_id, proxy=proxy_rule)
        self.assertTrue(ok)

        data = self.client.get_rule(rule_id)

        data['proxy']['retries'] = 111
        data['proxy']['upstream'][0]['weight'] = 9
        data['proxy']['backup_upstream'][0]['weight'] = 9
        ok = self.client.put_rule(rule_id=rule_id, proxy=data.get('proxy'))
        self.assertTrue(ok)

        self.__assert_proxy_rule(data, {
            'proxy': {
                'upstream': [{
                    'cluster': up_id,
                    'weight': 9,
                }],
                'backup_upstream': [{
                    'cluster': backup_up_id,
                    'weight': 9,
                }],
                'upstream_el_code': '',
                'retries': 111,
                'retry_condition': ['invalid_header', 'http_500'],
                'balancer': {
                    'algorithm': 'hash',
                    'variables': [
                        {'name': 'uri'},
                        {'name': 'uri-arg', 'args': 'foo'}
                    ]
                }
            }
        })

        data = self.client.get_all_rules_by_upstream_ip('172.22.31.2')
        self.assertEqual(len(data[self.app_id]), 1)
        self.assertEqual(data[self.app_id][0]['proxy']['retries'], 111)

        ok = self.client.del_rule(rule_id)
        self.assertTrue(ok)

        data = self.client.get_rule(rule_id)
        self.assertEqual(data, {})

        ok = self.client.del_upstream(up_id)
        self.assertTrue(ok)

        ok = self.client.del_upstream(backup_up_id)
        self.assertTrue(ok)

        data = self.client.get_upstream(backup_up_id)
        self.assertEqual(data, {})

    def __assert_upstream(self, upstream, expected):
        self.assertEqual(upstream['name'], expected['name'])

        for i, node in enumerate(upstream['nodes']):
            expected_node = expected['nodes'][i]
            for item in ('domain', 'port', 'status', 'ip', 'weight'):
                if expected_node.get(item):
                    self.assertEqual(node.get(item), expected_node.get(item))

        upstream_checker = upstream['checker']
        expected_checker = expected['checker']
        for item in ('interval', 'rise', 'http_req_uri'):
            self.assertEqual(upstream_checker.get(item),
                             expected_checker.get(item))

    def __assert_proxy_rule(self, proxy, expected):
        if 'upstream_el_code' in proxy['proxy']:
            self.assertEqual(proxy['proxy']['upstream_el_code'],
                        expected['proxy']['upstream_el_code'])
        else:
            for upstream_keyword in ('upstream', 'backup_upstream'):
                proxy_upstreams = proxy['proxy'][upstream_keyword]
                expected_upstreams = expected['proxy'][upstream_keyword]
                for i, proxy_upstream in enumerate(proxy_upstreams):
                    expected_upstream = expected_upstreams[i]
                    for item in ('cluster', 'weight'):
                        if expected_upstream.get(item):
                            self.assertEqual(proxy_upstream.get(item),
                                            expected_upstream.get(item))

        self.assertEqual(proxy['proxy']['retries'],
                         expected['proxy']['retries'])
        self.assertEqual(proxy['proxy']['retry_condition'],
                         expected['proxy']['retry_condition'])
        self.assertEqual(proxy['proxy']['balancer']['algorithm'],
                         expected['proxy']['balancer']['algorithm'])

        variables = proxy['proxy']['balancer']['variables']
        expected_vars = expected['proxy']['balancer']['variables']

        for i, variable in enumerate(variables):
            expected_var = expected_vars[i]
            for item in ('name', 'args'):
                if expected_var.get(item):
                    self.assertEqual(variable.get(item),
                                     expected_var.get(item))
