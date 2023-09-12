# -*- coding: utf-8 -*-
# import io
import sdk_test


class TestVersion(sdk_test.TestSdk):
    def test_get_version(self):
        data=self.client.get_version()
        self.assertGreater(data['admin_db_version'], 0)
        self.assertGreater(data['nginx_version'], 0)
        self.assertGreater(data['ngx_lua_version'], 0)
        self.assertGreater(data['required'], 0)
        self.assertGreater(data['version'], 0)
