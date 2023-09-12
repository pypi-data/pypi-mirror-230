# -*- coding: utf-8 -*-
# import io
import unittest
import sdk_test
import time


class TestStatus(sdk_test.TestSdk):
    def test_sync_status(self):
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

        changes = self.client.pending_changes()
        self.assertEqual(changes, 1)

        self.client.new_release()

        changes = self.client.pending_changes()
        self.assertEqual(changes, 0)

        time.sleep(1)
        total, synced = self.client.sync_status()
        self.assertEqual(total - synced, 0)

    def test_node_sync_status(self):
        data = self.client.node_sync_status()
        for node_id, node_info in data.items():
            node_id = int(node_id)
            self.assertGreater(node_id, 0)
            delay = node_info.get('delay', None)
            self.assertIs(type(delay), int)

    def test_get_all_waf_rules(self):
        condition = [{'var': 'client-country', 'op': 'eq', 'val': 'CN'}]
        cache_key = ['uri', 'query-string', 'client-city']
        cache_rule = {'cache_key': cache_key}
        rule_id = self.client.new_rule(condition=condition, cache=cache_rule,
                                       top=1)
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        condition = [{'var': 'uri', 'op': 'prefix', 'val': '/foo'}]
        waf_rule = {'rule_sets': [7,8,9,10,11,12,13,14,15,16,17],
                    'action': '403 Forbidden',
                    'threshold': 'low'}
        rule_id = self.client.new_rule(condition=condition,
                                       waf=waf_rule, last=True)
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        condition = [{'var': 'client-country', 'op': 'eq', 'val': 'JP'}]
        waf_rule = {'rule_sets': [7,8,9,10,11,12,13,14,15,16,17],
                    'action': '403 Forbidden', 'threshold': 'high'}
        rule_id = self.client.new_rule(condition=condition,
                                       waf=waf_rule, last=True)
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        data = self.client.get_all_rules()
        self.assertEqual(len(data), 3)

        data = self.client.get_all_waf_rules()
        self.assertEqual(len(data), 2)

        self.assertEqual(data[0]['waf']['threshold_score'], 1000)
        self.assertEqual(data[1]['waf']['threshold_score'], 10)

    @unittest.skip("deprecated api")
    def test_healthcheck_status(self):
        data = self.client.node_sync_status()
        for node_id, _ in data.items():
            node_id = int(node_id)
            # print(data)
            data = self.client.get_healthcheck_status(node_id)
            self.assertEqual(data, [])
