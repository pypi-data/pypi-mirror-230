# -*- coding: utf-8 -*-
# import io
import sdk_test


class TestApp(sdk_test.TestSdk):
    def test_app(self):
        app_id = self.app_id

        ok = self.client.put_app(app_id=app_id, domains=[self.apex],
                                 label=self.apex, cluster_groups=[1], offline=False)
        self.assertTrue(ok)

        self.client.new_release()

        ok = self.client.append_app_domain(app_id=app_id,
                                           domain='foo.' + self.apex)
        self.assertTrue(ok)

        data = self.client.get_app()

        self.assertEqual(data['name'], self.apex)
        self.assertEqual(data['partitions'], [1])
        self.assertEqual(data['domains'][0]['domain'], self.apex)
        self.assertEqual(data['domains'][1]['domain'], 'foo.' + self.apex)
        self.assertFalse(data['domains'][1]['is_wildcard'])

        limiter = {
            'max_uri_args': 120,
            'max_post_args': 130,
            'max_req_headers': 140
        }
        self.client.put_app_config(app_id=app_id, limiter=limiter, enable_websocket=True)
        self.client.new_release()
        config = self.client.get_app_config(app_id=app_id)
        self.assertEqual(config['limiter']['max_uri_args'], 120)
        self.assertEqual(config['limiter']['max_post_args'], 130)
        self.assertEqual(config['limiter']['max_req_headers'], 140)
        self.assertTrue(config['enable_websocket'])


    def test_search_app_by_domain_and_get_all_apps(self):
        app_id = self.app_id

        data = self.client.search_app(app_domain=self.apex)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], self.apex)
        self.assertEqual(data[0]['id'], app_id)

        new_app_id = self.client.new_app(domains=['prefix' + self.apex],
                                         label='prefix' + self.apex)
        self.assertIs(type(new_app_id), int)
        self.assertGreater(new_app_id, 0)

        data = self.client.search_app(app_domain=self.apex)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['domains'][0]['domain'], self.apex)
        self.assertEqual(data[0]['id'], app_id)
        self.assertEqual(data[1]['domains'][0]['domain'], 'prefix' + self.apex)
        self.assertEqual(data[1]['id'], new_app_id)

        apps = self.client.get_all_apps()
        for app in apps:
            self.assertIs(type(app), int)
            self.assertGreater(app, 0)

        apps = self.client.get_all_apps(detail=True)
        self.assertEqual(len(apps), 2)
        self.assertEqual(apps[app_id]['label'], self.apex)
        self.assertEqual(apps[app_id]['domains'][0]['domain'], self.apex)
        self.assertEqual(apps[new_app_id]['label'], 'prefix' + self.apex)
        self.assertEqual(apps[new_app_id]['domains'][0]['domain'],
                         'prefix' + self.apex)

        ok = self.client.del_app(new_app_id)
        self.assertTrue(ok)

        self.client.use_app(app_id)

