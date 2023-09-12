# -*- coding: utf-8 -*-
# import io
import sdk_test

class TestReferenced(sdk_test.TestSdk):
    def test_get_global_cert_referenced(self):
        data=self.client.get_global_cert_referenced(1)
        self.assertIs(type(data), list)
        self.assertTrue(len(data) >= 0)
