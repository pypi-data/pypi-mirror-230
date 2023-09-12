# -*- coding: utf-8 -*-
# import io
import sdk_test

class TestGlobalDymetrics(sdk_test.TestSdk):
    def test_global_dymetrics(self):
        sql = 'select status, count(*) from reqs group by status'
        dy_id = self.client.new_global_dymetrics(name='test', note='abc', interval=60, sql=sql)
        self.assertIs(type(dy_id), int)

        data = self.client.get_global_dymetrics(dy_id)
        self.assertEqual(data['name'], 'test')

        sql = 'select status, count(*) from reqs group by status'
        dy_id2 = self.client.new_global_dymetrics(name='test2', interval=120, sql=sql)
        self.assertIs(type(dy_id2), int)

        ok = self.client.put_global_dymetrics(dy_id, name='testput')
        self.assertTrue(ok)

        data = self.client.get_global_dymetrics(dy_id)
        self.assertEqual(data['name'], 'testput')

        data = self.client.get_global_dymetrics_data(dy_id)
        self.assertEqual(data, [])

        data = self.client.get_all_global_dymetrics()
        self.assertGreaterEqual(len(data), 2)

        ok = self.client.del_global_dymetrics(dy_id)
        self.assertTrue(ok)

        ok = self.client.del_global_dymetrics(dy_id2)
        self.assertTrue(ok)
