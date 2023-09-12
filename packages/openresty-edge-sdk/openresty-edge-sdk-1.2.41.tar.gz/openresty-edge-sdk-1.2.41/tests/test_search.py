# -*- coding: utf-8 -*-
# import io
import sdk_test
from datetime import datetime

class TestSearch(sdk_test.TestSdk):
    def test_search_app_by_upstream_ip(self):
        app_id = self.app_id

        up_id = self.client.new_upstream(
            name='origin-upstream',
            servers=[
                {'ip': '172.22.31.1', 'port': 80},
                {'ip': '172.22.31.2', 'port': 80, 'weight': 2}
            ])
        self.assertIs(type(up_id), int)
        self.assertGreater(up_id, 0)

        changes = self.client.pending_changes()
        self.assertEqual(changes, 1)

        new_app_id = self.client.new_app(domains=['prefix' + self.apex],
                                         label=self.apex)
        self.assertIs(type(app_id), int)
        self.assertGreater(app_id, 0)

        self.client.use_app(new_app_id)

        up_id = self.client.new_upstream(
            name='origin-upstream',
            servers=[
                {'ip': '172.22.31.1', 'port': 80},
                {'ip': '172.22.31.3', 'port': 80, 'weight': 2}
            ])
        self.assertIs(type(up_id), int)
        self.assertGreater(up_id, 0)

        data = self.client.search_app(upstream_ip='172.22.31.1')
        ok = self.client.del_app(new_app_id)
        self.assertTrue(ok)
        self.client.use_app(app_id)

        self.assertEqual(len(data), 2)
        self.assertEqual(data[1]['app']['domains'][0]['domain'], self.apex)
        self.assertEqual(data[1]['app']['id'], app_id)
        self.assertEqual(data[0]['app']['domains'][0]['domain'], 'prefix' + self.apex)
        self.assertEqual(data[0]['app']['id'], new_app_id)

        ok = self.client.del_upstream(up_id)
        self.assertTrue(ok)

    def test_req_rewrite(self):
        condition = [
            {'var': 'host', 'val': 'con.' + self.apex},
            {'var': ['req-header', 'Referer'],
             'vals': [[r'foo\d+', 'rx'], 'foo.com']}
        ]
        conseq = {
            'enable-websocket': {},
            'redirect': {'url': '/cn/2017/', 'code': 302}
        }
        rule_id = self.client.new_rule(condition=condition, conseq=conseq)
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        data = self.client.get_rule(rule_id)
        if data['actions'][0]['type'] == 'redirect':
            self.assertEqual(data['actions'][0]['redirect']['url'],
                             '/cn/2017/')
            self.assertEqual(data['actions'][1]['type'], 'enable-websocket')
        else:
            self.assertEqual(data['actions'][1]['redirect']['url'],
                             '/cn/2017/')
            self.assertEqual(data['actions'][0]['type'], 'enable-websocket')

        conseq['redirect']['url'] = '/cn/2018/'
        ok = self.client.put_rule(
            rule_id=rule_id, condition=condition, conseq=conseq)
        self.assertTrue(ok)
        data = self.client.get_rule(rule_id)
        if data['actions'][0]['type'] == 'redirect':
            self.assertEqual(data['actions'][0]['redirect']['url'],
                             '/cn/2018/')
        else:
            self.assertEqual(data['actions'][1]['redirect']['url'],
                             '/cn/2018/')

        ok = self.client.del_rule(rule_id)
        self.assertTrue(ok)
        data = self.client.get_rule(rule_id)
        self.assertEqual(data, {})


    def test_search_upstream(self):
        app_id = self.app_id

        up_id = self.client.new_upstream(
            name='app-upstream-' + datetime.now().strftime("%s"),
            servers=[
                {'ip': '172.22.31.1', 'port': 80},
                {'ip': '172.22.31.2', 'port': 80, 'weight': 2}
            ])
        self.assertIs(type(up_id), int)
        self.assertGreater(up_id, 0)

        changes = self.client.pending_changes()
        self.assertEqual(changes, 1)

        new_app_id = self.client.new_app(domains=['prefix' + self.apex],
                                         label=self.apex)
        self.assertIs(type(app_id), int)
        self.assertGreater(app_id, 0)

        global_up_id = self.client.new_global_upstream(
            name='global-upstream-' + datetime.now().strftime("%s"),
            servers=[
                {'ip': '172.22.31.1', 'port': 80},
                {'ip': '172.22.31.3', 'port': 80, 'weight': 2}
            ])

        self.assertIs(type(global_up_id), int)

        data = self.client.search_upstream_by_ip("172.22.31.1", 1, 1)
        self.assertEqual(len(data), 1)

        data = self.client.search_upstream_by_ip("172.22.31.1")
        self.assertEqual(len(data), 2)

        data = self.client.search_upstream_by_ip("172.22.31.2")
        self.assertEqual(len(data), 1)
        self.assertIn("app-upstream", data[0]['name'])

        data = self.client.search_upstream_by_ip("172.22.31.3")
        self.assertEqual(len(data), 1)
        self.assertIn("global-upstream", data[0]['name'])

        data = self.client.search_upstream_by_name("app-upstream")
        self.assertEqual(len(data), 1)
        self.assertIn("app-upstream", data[0]['name'])

        data = self.client.search_upstream_by_name("global-upstream")
        self.assertEqual(len(data), 1)
        self.assertIn("global-upstream", data[0]['name'])

        ok = self.client.del_global_upstream(global_up_id)
        self.assertTrue(ok)

        ok = self.client.del_upstream(up_id)
        self.assertTrue(ok)


    def test_search_http_app(self):

        new_app_id1 = self.client.new_app(domains=[datetime.now().strftime("%s") + ".domain.com"],
                                         label="label-name-" + datetime.now().strftime("%s"))
        self.assertIs(type(new_app_id1), int)
        self.assertGreater(new_app_id1, 0)

        new_app_id2 = self.client.new_app(domains=[datetime.now().strftime("%s") + ".domain2.com"],
                                         label="label2-name-" + datetime.now().strftime("%s"))
        self.assertIs(type(new_app_id2), int)
        self.assertGreater(new_app_id2, 0)

        data = self.client.search_http_app_by_keyword("domain", 1, 1)
        self.assertEqual(len(data), 1)

        data = self.client.search_http_app_by_keyword("domain")
        self.assertEqual(len(data), 2)

        data = self.client.search_http_app_by_keyword("domain2")
        self.assertEqual(len(data), 1)
        self.assertIn("label2-name", data[0]['name'])

        data = self.client.search_http_app_by_keyword("label-name")
        self.assertEqual(len(data), 1)
        self.assertIn("label-name", data[0]['name'])

        ok = self.client.del_app(new_app_id1)
        self.assertTrue(ok)

        ok = self.client.del_app(new_app_id2)
        self.assertTrue(ok)
