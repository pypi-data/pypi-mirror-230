# -*- coding: utf-8 -*-
# import io
import sdk_test


class TestCachePurge(sdk_test.TestSdk):
    def test_cache_purge(self):
        condition = [{'var': 'uri', 'op': 'prefix', 'val': '/foo'}]
        task_id = self.client.new_cache_purge_task(condition)
        self.assertIs(type(task_id), int)
        self.assertGreater(task_id, 0)

        data = self.client.get_cache_purge_task(task_id)
        self.assertEqual(data['type'], 'conditional')
        self.assertEqual(data['conditions'][0]['variable']['name'], 'uri')

        data = self.client.get_all_cache_purge_tasks()
        self.assertEqual(data[0]['type'], 'conditional')
        self.assertEqual(data[0]['conditions'][0]['variable']['name'], 'uri')

        ok = self.client.del_cache_purge_task(task_id)
        self.assertTrue(ok)
