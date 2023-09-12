# -*- coding: utf-8 -*-
import os
import string
import random
import time
import subprocess
import sdk_test

CURPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

class TestWafLogs(sdk_test.TestSdk):

    def test_get_waf_logs(self):
        init_waf_log_script = os.path.join(CURPATH, 'tests', 'init-waf-logs.sh')

        app_id = self.app_id

        command = "/usr/bin/bash {} {}".format(init_waf_log_script, app_id)
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
        self.assertEqual(result.returncode, 0)

        data, count = self.client.get_waf_logs(app_id)
        self.assertEqual(count, 3)
        self.assertEqual(len(data), count)

        data, count = self.client.get_waf_logs(app_id, show_all=True)
        self.assertEqual(count, 5)
        self.assertEqual(len(data), count)

        data, count = self.client.get_waf_logs(app_id, page=1, pagesize=2, show_all=True)
        self.assertEqual(count, 5)
        self.assertEqual(len(data), 2)

        data, count = self.client.get_waf_logs(app_id, page=2, pagesize=2, show_all=True)
        self.assertEqual(count, 5)
        self.assertEqual(len(data), 2)

        data, count = self.client.get_waf_logs(app_id, page=2, pagesize=2)
        self.assertEqual(count, 3)
        self.assertEqual(len(data), 1)

        current_time = time.time()

        start_time = current_time - 3600
        end_time = current_time + 3600
        data, count = self.client.get_waf_logs(app_id, start_time=start_time, end_time=end_time)
        self.assertEqual(count, 3)
        self.assertEqual(len(data), 3)

        start_time = current_time - 3600
        end_time = current_time - 1800
        data, count = self.client.get_waf_logs(app_id, start_time=start_time, end_time=end_time)
        self.assertEqual(count, 0)
        self.assertEqual(data, None)

        start_time = current_time + 1800
        end_time = current_time + 3600
        data, count = self.client.get_waf_logs(app_id, start_time=start_time, end_time=end_time)
        self.assertEqual(count, 0)
        self.assertEqual(data, None)

        host="test.com"
        data, count = self.client.get_waf_logs(app_id, host=host)
        self.assertEqual(count, 3)
        self.assertEqual(len(data), 3)

        host="test2.com"
        data, count = self.client.get_waf_logs(app_id, host=host)
        self.assertEqual(count, 0)
        self.assertEqual(data, None)

        header="Host: test.com"
        data, count = self.client.get_waf_logs(app_id, header=header)
        self.assertEqual(count, 3)
        self.assertEqual(len(data), 3)

        header="Host: test2.com"
        data, count = self.client.get_waf_logs(app_id, header=header)
        self.assertEqual(count, 0)
        self.assertEqual(data, None)

        rule_set_id=15
        data, count = self.client.get_waf_logs(app_id, rule_set_id=rule_set_id)
        self.assertEqual(count, 3)
        self.assertEqual(len(data), 3)

        rule_set_id=1
        data, count = self.client.get_waf_logs(app_id, rule_set_id=rule_set_id)
        self.assertEqual(count, 0)
        self.assertEqual(data, None)

        data, count = self.client.get_waf_logs(app_id, resp_status=403)
        self.assertEqual(count, 3)
        self.assertEqual(len(data), 3)

        data, count = self.client.get_waf_logs(app_id, resp_status=200)
        self.assertEqual(count, 0)
        self.assertEqual(data, None)

        action = "block"
        data, count = self.client.get_waf_logs(app_id, action=action)
        self.assertEqual(count, 3)
        self.assertEqual(len(data), 3)

        action = "edge-captcha"
        data, count = self.client.get_waf_logs(app_id, action=action)
        self.assertEqual(count, 0)
        self.assertEqual(data, None)

        remote_addr = "127.0.0.1"
        data, count = self.client.get_waf_logs(app_id, remote_addr=remote_addr)
        self.assertEqual(count, 3)
        self.assertEqual(len(data), 3)

        remote_addr = "127.0.0.2"
        data, count = self.client.get_waf_logs(app_id, remote_addr=remote_addr)
        self.assertEqual(count, 0)
        self.assertEqual(data, None)

        try:
            request_id = "00000580000455aad5e00000"
            data, count = self.client.get_waf_logs(app_id, request_id=request_id)
            self.assertEqual(count, 1)
            self.assertEqual(len(data), 1)
        except Exception as e:
            self.assertEqual(e.args[0], 'request id 00000580000455aad5e00000 does not belong to app {}, but belongs to 1'.format(app_id))
