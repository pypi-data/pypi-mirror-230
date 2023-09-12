# -*- coding: utf-8 -*-
# import io
import sdk_test
import string
import random

class TestParitionLuaModule(sdk_test.TestSdk):
    def test_partition_lua_module(self):
        data = self.client.get_all_partition_lua_module(1)
        self.assertIs(type(data), list)
        self.assertTrue(len(data) >= 0)

        data = self.client.get_partition_lua_module(1, 1000000)
        self.assertEqual(data, {})

        code = """
        local _M = {}

        _M.test = 1

        return _M
        """
        pname = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 6))
        name = "test" + pname
        data = self.client.new_partition_lua_module(1, name, code)
        id = data["id"]
        self.assertIs(type(id), int)

        data = self.client.get_all_partition_lua_module(1)
        self.assertTrue(len(data) > 0)

        new_name = "test2" + pname
        data = self.client.put_partition_lua_module(1, id, new_name)
        self.assertEqual(data, True)

        new_code = """
        local _M = {}

        _M.test = 2

        return _M
        """
        data = self.client.put_partition_lua_module(1, id, None, new_code)
        self.assertEqual(data, True)

        data = self.client.get_partition_lua_module(1, id)
        self.assertEqual(data["id"], id)
        self.assertEqual(data["name"], new_name)
        self.assertEqual(data["code"], new_code)

        data = self.client.del_partition_lua_module(1, id)
        self.assertEqual(data, True)
