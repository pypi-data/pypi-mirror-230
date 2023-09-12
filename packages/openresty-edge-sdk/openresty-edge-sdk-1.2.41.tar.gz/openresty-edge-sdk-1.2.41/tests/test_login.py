# -*- coding: utf-8 -*-
import os
import sys
import random
import sdk_test


CURPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
HOST = os.getenv('EDGE_HOST')
USER_NAME = os.getenv('EDGE_USER')
PASSWORD = os.getenv('EDGE_PASSWORD')
sys.path.insert(0, CURPATH)


from edge2client import Edge2Client


class TestLogin(sdk_test.TestSdk):
    def test_login(self):
        ok = self.client.login()
        self.assertTrue(ok)
        if sys.version_info.major == 3:
            self.assertRegex(self.client.get_token(), r'^\S{32,}$')
        else:
            self.assertRegexpMatches(self.client.get_token(), r'^\S{32,}$')

    def test_login_with_wrong_username(self):
        client = Edge2Client(HOST, USER_NAME + 'wrong', PASSWORD)
        with self.assertRaises(Exception) as cm:
            client.login()

        self.assertEqual(str(cm.exception),
                         'failed to login: incorrect login credentials')
