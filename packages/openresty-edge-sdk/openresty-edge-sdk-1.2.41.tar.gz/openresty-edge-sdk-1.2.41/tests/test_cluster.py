# -*- coding: utf-8 -*-
# import io
import os
import sdk_test


CURPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


class TestCluster(sdk_test.TestSdk):
    def test_cluster_group(self):
        group_id = self.client.new_cluster_group('test')
        self.assertIs(type(group_id), int)
        self.assertGreater(group_id, 0)

        ok = self.client.put_cluster_group(group_id=group_id, group_name='foo')
        self.assertTrue(ok)

        data = self.client.get_cluster_group(group_id)
        self.assertEqual(data['id'], group_id)
        self.assertEqual(data['name'], 'foo')

        data = self.client.get_all_cluster_groups()
        self.assertEqual(len(data), 2)

        ok = self.client.del_cluster_group(group_id)
        self.assertTrue(ok)

        data = self.client.get_cluster_group(group_id)
        self.assertEqual(data, {})
