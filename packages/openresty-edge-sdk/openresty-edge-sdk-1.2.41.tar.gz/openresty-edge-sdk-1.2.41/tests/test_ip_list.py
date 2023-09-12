# -*- coding: utf-8 -*-
# import io
import sdk_test


class TestIPList(sdk_test.TestSdk):
    def test_ip_list(self):
        # create
        rule_id = self.client.new_ip_list(name='ip_list_1', items=[{'ip': '127.0.0.1'}])
        self.assertIsInstance(rule_id, int)

        # get
        ip_list_1 = self.client.get_ip_list(rule_id)
        self.assertEqual(ip_list_1.get('name'), 'ip_list_1')

        # modify
        self.client.put_ip_list(rule_id=rule_id, items=[{'ip': '192.168.1.1'}])
        ip_list_1 = self.client.get_ip_list(rule_id)
        self.assertEqual(ip_list_1.get('items')[0].get('ip'), '192.168.1.1')

        # delete
        ok = self.client.del_ip_list(rule_id=rule_id)
        self.assertTrue(ok)

    def test_global_ip_list(self):
        # create
        global_rule_id = self.client.new_global_ip_list(name='g_ip_list_1',
                                                        items=[{'ip': '127.0.0.2'}])
        self.assertIsInstance(global_rule_id, int)

        # get
        g_ip_list_1 = self.client.get_global_ip_list(global_rule_id)
        self.assertEqual(g_ip_list_1.get('name'), 'g_ip_list_1')

        # modify
        self.client.put_global_ip_list(rule_id=global_rule_id,
                                       items=[{'ip': '192.168.1.2'}])
        g_ip_list_1 = self.client.get_global_ip_list(global_rule_id)
        self.assertEqual(g_ip_list_1.get('items')[0].get('ip'), '192.168.1.2')

        # delete
        ok = self.client.del_global_ip_list(rule_id=global_rule_id)
        self.assertTrue(ok)
