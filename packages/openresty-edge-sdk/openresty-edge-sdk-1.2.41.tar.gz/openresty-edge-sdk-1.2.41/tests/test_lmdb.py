# -*- coding: utf-8 -*-
# import io
import sdk_test

class TestLMDB(sdk_test.TestSdk):
    def test_lmdb_backup(self):
        result = self.client.lmdb_backup()
        if result is not True:
            self.assertIs(type(result), dict)
        else:
            self.assertIs(type(result), bool)
