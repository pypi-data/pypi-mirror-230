# -*- coding: utf-8 -*-
# import io
import sdk_test

class TestAppMetrics(sdk_test.TestSdk):
    def test_app_metrics(self):
        data = self.client.get_app_metrics(self.app_id)
        self.assertEqual(data, [])
