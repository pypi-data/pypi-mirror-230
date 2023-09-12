# -*- coding: utf-8 -*-
# import io
import sdk_test


class TestNodes(sdk_test.TestSdk):
    def test_get_all_nodes(self):
        data=self.client.get_all_nodes()
        self.assertEqual(type(data), type(list()))

        if len(data) == 0:
            return

        node = data[0]
        self.assertEqual(type(node), type({}))
        self.assertEqual(type(node['id']), type(1))
        self.assertEqual(type(node['gateway_id']), type(1))
        node_id = node['id']
        gateway_id = node['gateway_id']

        # test get_node
        node = self.client.get_node(node_id)
        self.assertEqual(type(node), type({}))

        node = self.client.get_node(node_id, gateway_id=gateway_id)
        self.assertEqual(type(node), type({}))

        # test put_node
        ok = self.client.put_node(node_id, \
            gateway_id=gateway_id, name='test', \
            is_gray=True, status=2, external_ip='127.0.0.1', \
            external_ipv6='::1', internal_ip='127.0.0.1')

        self.assertEqual(ok, True)

        node = self.client.get_node(node_id, gateway_id=gateway_id)
        self.assertEqual(type(node), type({}))
        self.assertEqual(node['name'], 'test')
        self.assertEqual(node['is_gray'], True)
        self.assertEqual(node['status'], 2)
        self.assertEqual(node['external_ip'], '127.0.0.1')
        self.assertEqual(node['external_ipv6'], '::1')
        self.assertEqual(node['internal_ip'], '127.0.0.1')

        # test put_node 2
        ok = self.client.put_node(node_id, \
            gateway_id=gateway_id, name='test2', \
            is_gray=False, status=1, external_ip='127.0.0.2', \
            external_ipv6='::2', internal_ip='127.0.0.2')

        self.assertEqual(ok, True)

        node = self.client.get_node(node_id, gateway_id=gateway_id)
        self.assertEqual(type(node), type({}))
        self.assertEqual(node['name'], 'test2')
        self.assertEqual(node['is_gray'], False)
        self.assertEqual(node['status'], 1)
        self.assertEqual(node['external_ip'], '127.0.0.2')
        self.assertEqual(node['external_ipv6'], '::2')
        self.assertEqual(node['internal_ip'], '127.0.0.2')
