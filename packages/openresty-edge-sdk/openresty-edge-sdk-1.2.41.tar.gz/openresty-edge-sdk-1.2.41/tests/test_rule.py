# -*- coding: utf-8 -*-
# import io
import os
import random
import sdk_test


CURPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


class TestRule(sdk_test.TestSdk):
    def test_waf(self):
        condition = [{'var': 'uri', 'op': 'prefix', 'val': '/foo'}]
        waf_rule = {'rule_sets': [7,8,9,10,11,12,13,14,15,16,17],
                    'action': '403 Forbidden', 'threshold': 'low'}
        rule_id = self.client.new_rule(condition=condition,
                                       waf=waf_rule, last=True)
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        waf_rule = {'rule_sets': [7,8,9,10,11,12,13,14,15,16,17],
                    'action': '403 Forbidden', 'threshold': 'high'}
        ok = self.client.put_rule(rule_id=rule_id, waf=waf_rule,
                                  condition=condition)
        self.assertTrue(ok)

        data = self.client.get_rule(rule_id)
        self.assertIn(7, data['waf']['rule_sets'])
        self.assertIn(8, data['waf']['rule_sets'])
        self.assertEqual(data['waf']['threshold_score'], 1000)

        waf_rule = {'rule_sets': [7,8,9,10,11,12,13,14,15,16,17],
                    'action': 'log'}
        ok = self.client.put_rule(rule_id=rule_id, waf=waf_rule,
                                  condition=condition)
        self.assertTrue(ok)

        waf_rule = {'rule_sets': [7,8,9,10,11,12,13,14,15,16,17],
                    'action': 'edge-captcha', 'threshold': 'low',
                    'clearance': 60}
        ok = self.client.put_rule(rule_id=rule_id, waf=waf_rule,
                                  condition=condition)
        self.assertTrue(ok)

        waf_rule = {'rule_sets': [7,8,9,10,11,12,13,14,15,16,17],
                    'action': 'redirect', 'threshold': 'medium',
                    'redirect_url': 'https://openrsty.org'}
        ok = self.client.put_rule(rule_id=rule_id, waf=waf_rule,
                                  condition=condition)
        self.assertTrue(ok)

        ok = self.client.del_rule(rule_id)
        self.assertTrue(ok)

        data = self.client.get_rule(rule_id)
        self.assertEqual(data, {})

    def test_cache(self):
        condition = [{'var': 'client-country', 'op': 'eq', 'val': 'CN'}]
        cache_key = ['uri', 'query-string', 'client-city']
        cache_rule = {'cache_key': cache_key}
        rule_id = self.client.new_rule(condition=condition, cache=cache_rule)
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        condition[0]['val'] = 'JP'
        cache_key = [
            {'name': "uri", },
            {'name': "client-city"},
            {'name': "client-continent", 'args': 'first-x-forwarded-addr'},
            {'name': "query-string"}
        ]
        default_ttls= [{
            'ttl_unit': "min", 'status': 200, 'ttl': 2
        }, {
            'ttl_unit': "min", 'status': 301, 'ttl': 1
        }]
        cache_rule = {
            'cache_key': cache_key,
            'default_ttls': default_ttls,
            'browser_ttl': 2,
            'browser_ttl_unit': 'min',
            'disable_convert_head': False,
            'enforce_cache': True,
            'cluster_hash': True,
            'enable_global': True,
        }
        ok = self.client.put_rule(rule_id=rule_id, condition=condition,
                                  cache=cache_rule)
        self.assertTrue(ok)

        data = self.client.get_rule(rule_id)
        self.assertEqual(data['cache']['cache_key'][0]['name'], 'uri')
        self.assertEqual(data['cache']['cache_key'][1]['name'], 'client-city')
        self.assertEqual(data['cache']['cache_key'][2]['args'], 'first-x-forwarded-addr')
        self.assertEqual(len(data['cache']['cache_key']), 4)
        self.assertEqual(data['cache']['cluster_hash'], True)
        self.assertEqual(data['cache']['disable_convert_head'], False)
        self.assertEqual(data['cache']['enforce_cache'], True)
        self.assertEqual(data['cache']['enable_global'], True)
        self.assertEqual(data['cache']['browser_ttl'], 2)
        self.assertEqual(data['cache']['browser_ttl_unit'], 'min')
        self.assertEqual(type(data['cache']['default_ttls']), type(list()))
        self.assertEqual(data['conditions'][0]['values'][0]['val'], 'JP')

        ok = self.client.del_rule(rule_id)
        self.assertTrue(ok)

        data = self.client.get_rule(rule_id)
        self.assertEqual(data, {})

    def test_content(self):
        condition = [{'var': 'uri', 'op': 'eq', 'val': '/favicon.ico'}]
        file_id = self.client.upload_favicon(name='test',
                                             favicon_content='content')
        self.assertIs(type(file_id), int)
        self.assertGreater(file_id, 0)

        rule_id = self.client.new_rule(condition=condition,
                                       content={'favicon': file_id})
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        new_file_id = self.client.upload_favicon(
            name='test',
            favicon_content='new_content')
        self.assertIs(type(new_file_id), int)
        self.assertGreater(new_file_id, 0)

        ok = self.client.put_rule(rule_id=rule_id,
                                  content={'favicon': new_file_id})
        self.assertTrue(ok)

        data = self.client.get_rule(rule_id)

        self.assertEqual(data['content']['file'], new_file_id)
        self.assertEqual(data['conditions'][0]['values'][0]['val'],
                         '/favicon.ico')

        ok = self.client.del_rule(rule_id)
        self.assertTrue(ok)

        ok = self.client.del_favicon(file_id)
        ok = self.client.del_favicon(new_file_id)
        self.assertTrue(ok)

        data = self.client.get_rule(rule_id)
        self.assertEqual(data, {})

    def test_empty_gif(self):
        condition = [{'var': 'uri', 'op': 'eq', 'val': '/'}]
        rule_id = self.client.new_rule(condition=condition,
                                       content={'empty_gif': True})
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        data = self.client.get_rule(rule_id)
        self.assertTrue(data['content']['empty_gif'])

        ok = self.client.del_rule(rule_id)
        self.assertTrue(ok)

        data = self.client.get_rule(rule_id)
        self.assertEqual(data, {})

    def test_get_all_rules(self):
        condition = [{'var': 'client-country', 'op': 'eq', 'val': 'CN'}]
        cache_key = ['uri', 'query-string', 'client-city']
        cache_rule = {'cache_key': cache_key}
        rule_id = self.client.new_rule(condition=condition, cache=cache_rule,
                                       top=1)
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        condition = [
            {'var': 'host', 'val': 'con.' + self.apex},
            {'var': ['req-header', 'Referer'],
             'vals': [[r'foo\d+', 'rx'], 'foo.com']}
        ]
        conseq = {
            'enable-websocket': {},
            'redirect': {'url': '/cn/2017/', 'code': 302},
            'user-code': {'el': 'true => say(\"hello\");'}
        }
        rule_id = self.client.new_rule(condition=condition, conseq=conseq,
                                       last=True)
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        data = self.client.get_all_rules()
        self.assertEqual(len(data), 2)

        self.assertEqual(data[0]['top'], 1)
        self.assertTrue(data[1]['last'])

        data = self.client.get_all_rules_by_app_domain(self.apex)
        self.assertEqual(len(data), 2)

    def test_el(self):
        code = "true => print('hello, {}');".format(self.apex)
        ok = self.client.new_el(phase='req-rewrite', code=code, pre=True)
        self.assertTrue(ok)

    def test_cert(self):
        domain = str(random.randint(1, 10000)) + '.foo.com'
        ok = self.client.put_app(app_id=self.app_id, domains=[domain],
                                 label='foo.com')
        self.assertTrue(ok)

        self.client.new_release()

        key_file = os.path.join(CURPATH, 'tests', 'key.pem')
        cert_file = os.path.join(CURPATH, 'tests', 'cert.pem')
        with open(key_file) as f:
            key = f.read()
        with open(cert_file) as f:
            cert = f.read()

        cert_id = self.client.set_cert_key(key=key, cert=cert)
        self.assertIs(type(cert_id), int)
        self.assertGreater(cert_id, 0)

        data = self.client.get_cert_key(cert_id)
        self.assertEqual(data['domains'][0], '*.foo.com')

        data = self.client.get_all_cert_keys()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['domains'], ['*.foo.com'])

        ok = self.client.del_cert_key(cert_id)
        self.assertTrue(ok)

        data = self.client.get_cert_key(cert_id)
        self.assertEqual(data, {})

    def test_req_rewrite_3(self):
        condition = [
            {'var': 'host', 'val': 'con.' + self.apex},
            {'var': 'server-port', 'op': 'is-empty'},
        ]
        conseq = {
            'enable-websocket': {},
            'redirect': {'url': '/cn/2017/', 'code': 302}
        }
        rule_id = self.client.new_rule(condition=condition, conseq=conseq)
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        data = self.client.get_rule(rule_id)
        self.assertEqual(data['conditions'][0]['variable']['name'], 'host')
        self.assertEqual(data['conditions'][1]['variable']['name'],
                         'server-port')
        self.assertEqual(data['conditions'][1]['operator']['name'], 'is-empty')

        ok = self.client.del_rule(rule_id)
        self.assertTrue(ok)
        data = self.client.get_rule(rule_id)
        self.assertEqual(data, {})

    def test_rule_order(self):
        condition = [{'var': 'uri', 'op': 'eq', 'val': '/favicon.ico'}]
        file_id = self.client.upload_favicon(name='test',
                                             favicon_content='content')
        self.assertIs(type(file_id), int)
        self.assertGreater(file_id, 0)

        rule_id = self.client.new_rule(condition=condition,
                                       content={'favicon': file_id})
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        new_file_id = self.client.upload_favicon(
            name='test',
            favicon_content='new_content')
        self.assertIs(type(new_file_id), int)
        self.assertGreater(new_file_id, 0)

        ok = self.client.put_rule(rule_id=rule_id,
                                  content={'favicon': new_file_id},
                                  order=1)
        self.assertTrue(ok)

        data = self.client.get_rule(rule_id)
        self.assertEqual(data['order'], 1)

        ok = self.client.del_rule(rule_id)
        self.assertTrue(ok)

        ok = self.client.del_favicon(file_id)
        ok = self.client.del_favicon(new_file_id)
        self.assertTrue(ok)
