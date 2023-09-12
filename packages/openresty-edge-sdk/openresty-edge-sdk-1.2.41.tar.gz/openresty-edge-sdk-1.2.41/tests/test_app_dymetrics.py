# -*- coding: utf-8 -*-
# import io
import sdk_test

class TestAppDymetrics(sdk_test.TestSdk):
    def test_app_dymetrics(self):
        app_id = self.app_id

        sql = 'select status, count(*) from reqs group by status'
        dy_id = self.client.new_app_dymetrics(app_id=app_id, name='test', note='abc', interval=60, sql=sql)
        self.assertIs(type(dy_id), int)

        data = self.client.get_app_dymetrics(app_id, dy_id)
        self.assertEqual(data['name'], 'test')

        sql = 'select status, count(*) from reqs group by status'
        dy_id2 = self.client.new_app_dymetrics(app_id=app_id, name='test2', interval=120, sql=sql)
        self.assertIs(type(dy_id2), int)

        ok = self.client.put_app_dymetrics(app_id, dy_id, name='testput')
        self.assertTrue(ok)

        data = self.client.get_app_dymetrics(app_id, dy_id)
        self.assertEqual(data['name'], 'testput')

        data = self.client.get_app_dymetrics_data(app_id, dy_id)
        self.assertEqual(data, [])

        data = self.client.get_all_app_dymetrics(app_id)
        self.assertGreaterEqual(len(data), 2)

        ok = self.client.del_app_dymetrics(app_id, dy_id)
        self.assertTrue(ok)

        ok = self.client.del_app_dymetrics(app_id, dy_id2)
        self.assertTrue(ok)
