# -*- coding: utf-8 -*-
# import io
import os
import string
import random
import sdk_test


CURPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


class TestGlobalRule(sdk_test.TestSdk):
    def test_global_cert(self):
        key_file = os.path.join(CURPATH, 'tests', 'short_test.key')
        cert_file = os.path.join(CURPATH, 'tests', 'short_test.crt')
        with open(key_file) as f:
            key = f.read()
        with open(cert_file) as f:
            cert = f.read()

        cert_id = self.client.set_global_cert_key(key=key, cert=cert)
        self.assertIs(type(cert_id), int)
        self.assertGreater(cert_id, 0)

        data = self.client.get_global_cert_key(cert_id)
        self.assertEqual(data['domains'][0], 'test.com')

        key_file = os.path.join(CURPATH, 'tests', 'test.key')
        cert_file = os.path.join(CURPATH, 'tests', 'test.crt')
        with open(key_file) as f:
            key = f.read()
        with open(cert_file) as f:
            cert = f.read()

        ok = self.client.put_global_cert_key(cert_id=cert_id,
                                             key=key, cert=cert)
        self.assertTrue(ok)

        data = self.client.get_global_cert_key(cert_id)
        self.assertEqual(data['domains'][0], 'test.com')

        ok = self.client.del_global_cert_key(cert_id)
        self.assertTrue(ok)

        data = self.client.get_global_cert_key(cert_id)
        self.assertEqual(data, {})

    def test_global_user(self):
        app_id = self.app_id
        only_reader = ''.join([random.choice(string.ascii_letters)
                               for n in range(10)])
        pwd = ''.join([random.choice(string.ascii_letters + string.digits)
                       for n in range(12)])

        ok = self.client.add_global_user(
            name=only_reader, pwd=pwd, gid=[1])
        self.assertTrue(ok)

        ok = self.client.add_global_user(
            name='prefix_' + only_reader, pwd=pwd, gid=[1])
        self.assertTrue(ok)

        data = self.client.search_global_user('not_exist' + only_reader)
        user_id = data.get('id')
        self.assertEqual(user_id, None)

        data = self.client.search_global_user(only_reader)
        user_id = data.get('id')
        self.assertIs(type(user_id), int)
        self.assertGreater(user_id, 0)

        users = self.client.get_all_global_users()
        for global_user_id in users:
            self.assertIs(type(global_user_id), int)
            self.assertGreater(global_user_id, 0)

        user_id = self.client.add_app_user(name='not_exist' + only_reader)
        self.assertEqual(user_id, 'no "not_exist{}" user found'
                         .format(only_reader))

        user_id = self.client.add_app_user(name=only_reader)
        self.assertIs(type(user_id), int)
        self.assertGreater(user_id, 0)

        ok = self.client.put_app_user(id=user_id, name=only_reader,
                                      release=True)
        self.assertTrue(ok)

        data = self.client.get_app_user(id=user_id)
        self.assertTrue(data['id'], user_id)
        self.assertTrue(data['uid'], user_id)
        self.assertTrue(data['release'])
        self.assertTrue(data['write'])

        data = self.client.get_app_user(name=only_reader)
        self.assertTrue(data['id'], user_id)
        self.assertTrue(data['uid'], user_id)
        self.assertTrue(data['release'])
        self.assertTrue(data['write'])

        data = self.client.get_app_user(name='not_exist' + only_reader)
        self.assertEqual(data, {})

        data = self.client.get_app_user(user_id + 1)
        self.assertEqual(data, {})

        data = self.client.get_all_app_users()
        self.assertEqual(data[0]['username'], only_reader)
        self.assertTrue(data[0]['release'])
        self.assertTrue(data[0]['write'])

        ok = self.client.del_app_user(name=only_reader)
        self.assertTrue(ok)

        new_app_id = self.client.new_app(domains=['prefix' + self.apex],
                                         label=self.apex)

        ok = self.client.add_user_for_all_apps(name=only_reader)
        self.assertTrue(ok)

        data = self.client.get_all_app_users()
        self.assertEqual(data[0]['username'], only_reader)

        data = self.client.get_all_app_users(app_id=new_app_id)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['username'], only_reader)

        ok = self.client.del_app_user(name=only_reader)
        self.assertTrue(ok)

        data = self.client.get_all_app_users()
        self.assertEqual(len(data), 0)

        ok = self.client.del_app(new_app_id)
        self.assertTrue(ok)

        new_app_id = self.client.new_app(domains=['prefix' + self.apex],
                                         label=self.apex)
        self.client.use_app(new_app_id)
        ok = self.client.add_all_users_for_app()
        self.assertTrue(ok)

        data = self.client.get_all_app_users()
        self.assertGreater(len(data), 4)

        ok = self.client.del_app(new_app_id)
        self.assertTrue(ok)

        self.client.use_app(app_id)

    def test_global_rule(self):
        condition = [
            {'var': 'host', 'val': 'con.' + self.apex},
            {'var': ['req-header', 'Referer'],
             'vals': [[r'foo\d+', 'rx'], 'foo.com']}
        ]
        conseq = {
            'enable-websocket': {},
            'redirect': {'url': '/cn/2017/', 'code': 302}
        }
        rule_id = self.client.new_global_rule(condition=condition,
                                              conseq=conseq)
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        data = self.client.get_global_rule(rule_id)
        if data['actions'][0]['type'] == 'redirect':
            self.assertEqual(data['actions'][0]['redirect']['url'],
                             '/cn/2017/')
            self.assertEqual(data['actions'][1]['type'], 'enable-websocket')
        else:
            self.assertEqual(data['actions'][1]['redirect']['url'],
                             '/cn/2017/')
            self.assertEqual(data['actions'][0]['type'],
                             'enable-websocket')

        conseq['redirect']['url'] = '/cn/2018/'
        ok = self.client.put_global_rule(rule_id=rule_id, condition=condition,
                                         conseq=conseq)
        self.assertTrue(ok)
        data = self.client.get_global_rule(rule_id)
        if data['actions'][0]['type'] == 'redirect':
            self.assertEqual(data['actions'][0]['redirect']['url'],
                             '/cn/2018/')
        else:
            self.assertEqual(data['actions'][1]['redirect']['url'],
                             '/cn/2018/')

        data = self.client.get_all_global_rules()
        self.assertEqual(len(data), 1)
        data = data[0]
        if data['actions'][0]['type'] == 'redirect':
            self.assertEqual(data['actions'][0]['redirect']['url'],
                             '/cn/2018/')
        else:
            self.assertEqual(data['actions'][1]['redirect']['url'],
                             '/cn/2018/')

        ok = self.client.del_global_rule(rule_id)
        self.assertTrue(ok)
        data = self.client.get_global_rule(rule_id)
        self.assertEqual(data, {})

    def test_global_var(self):
        random_name = ''.join([random.choice(string.ascii_letters)
                               for n in range(10)])
        name = 'is-whitelist-' + random_name
        var_id = self.client.new_global_var(name=name, var_type='string',
                                            default='no')
        self.assertIs(type(var_id), int)
        self.assertGreater(var_id, 0)

        condition = [
            {'global_var': var_id, 'vals': ['no']}
        ]
        conseq = {
            'limit-req-rate': {'limit_key': 'uri', 'rate_shape': 1,
                               'rate_reject': 1, 'rate_shape_unit': 'r/min',
                               'rate_reject_unit': 'r/min'}
        }
        rule_id = self.client.new_global_rule(condition=condition,
                                              conseq=conseq)
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        ok = self.client.put_global_var(var_id=var_id, name=name,
                                        var_type='string', default='yes')
        self.assertTrue(ok)

        data = self.client.get_global_var(var_id)
        self.assertEqual(data['default'], 'yes')
        self.assertEqual(data['name'], name)

        ok = self.client.del_global_rule(rule_id)
        self.assertTrue(ok)

        ok = self.client.del_global_var(var_id)
        self.assertTrue(ok)

    def test_global_ngx_config(self):
        config = {'keepalive_timeout': 10, 'enable_open_file_cache': False}
        ok = self.client.set_global_ngx_config(config)
        self.assertTrue(ok)

        data = self.client.get_global_ngx_config()
        self.assertEqual(data['keepalive_timeout'], 10)
        self.assertFalse(data['enable_open_file_cache'])

    def test_request_id(self):
        ok = self.client.disable_request_id()
        self.assertTrue(ok)

        status = self.client.get_request_id_status()
        self.assertFalse(status)

        ok = self.client.enable_request_id()
        self.assertTrue(ok)

        status = self.client.get_request_id_status()
        self.assertTrue(status)

        data = self.client.get_global_misc_config()
        self.assertTrue(data['enabled_req_id'])

        ok = self.client.disable_request_id()
        self.assertTrue(ok)

        status = self.client.get_request_id_status()
        self.assertFalse(status)

        ok = self.client.set_global_misc_config({'enabled_req_id': True})
        self.assertTrue(ok)

        data = self.client.get_global_misc_config()
        self.assertTrue(data['enabled_req_id'])

        ok = self.client.disable_request_id()
        self.assertTrue(ok)

    def test_global_waf_rule(self):
        data = self.client.get_all_global_waf_rules()
        for rule in data:
            rule_id = rule['id']
            if rule_id > 10000:
                self.client.del_global_waf_rule(rule_id)

        # add global user defined waf user
        waf_rule_id = self.client.new_global_waf_rule(
            name='foo',
            code='''uri-arg('foo') =>
    waf-mark-risk(level: 'definite', msg: 'found foo');''')
        self.assertIs(type(waf_rule_id), int)
        self.assertGreater(waf_rule_id, 0)

        ok = self.client.put_global_waf_rule(
            rule_id=waf_rule_id, name='bar',
            code='''uri-arg('bar') =>
    waf-mark-risk(level: 'definite', msg: 'found bar');''')
        self.assertTrue(ok)

        data = self.client.get_global_waf_rule(waf_rule_id)
        self.assertEqual(data['name'], 'bar')
        self.assertEqual(data['code'], '''uri-arg('bar') =>
    waf-mark-risk(level: 'definite', msg: 'found bar');''')

        # add new rewrite rule without user defined waf rules
        condition = [{'var': 'uri', 'op': 'prefix', 'val': '/foo'}]
        waf_rule = {'rule_sets': [7,8,9,10,11,12,13,14,15,16,17],
                    'action': '403 Forbidden',
                    'threshold': 'low'}
        rule_id = self.client.new_rule(condition=condition,
                                       waf=waf_rule, last=True)
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        data = self.client.get_rule(rule_id)
        self.assertIn(7, data['waf']['rule_sets'])
        self.assertIn(8, data['waf']['rule_sets'])
        self.assertNotIn(waf_rule_id, data['waf']['rule_sets'])

        # update rewrite rule with user defined waf rules
        waf_rule = {'rule_sets': [waf_rule_id], 'action': '403 Forbidden',
                    'threshold': 'high'}
        ok = self.client.put_rule(rule_id=rule_id,
                                  waf=waf_rule, condition=condition)
        self.assertTrue(ok)

        data = self.client.get_rule(rule_id)
        # self.assertIn(2, data['waf']['rule_sets'])
        # self.assertIn(3, data['waf']['rule_sets'])
        self.assertIn(waf_rule_id, data['waf']['rule_sets'])
        self.assertEqual(data['waf']['threshold_score'], 1000)

        ok = self.client.del_rule(rule_id)
        self.assertTrue(ok)

        ok = self.client.del_global_waf_rule(waf_rule_id)
        self.assertTrue(ok)

    def test_req_rewrite_2(self):
        condition = [
            {'var': 'host', 'val': 'con.' + self.apex},
            {'var': ['req-header', 'Referer'],
             'vals': [[r'foo\d+', 'rx'], 'foo.com']}
        ]
        conseq = [
            {'set-proxy-header': {
                'header': 'Foo',
                'value': 'default',
            }},
            {'set-proxy-header': {
                'header': 'Host',
                'value': "orig",
            }},
            {'print': {
                'msg': 'hello'
            }}
        ]
        rule_id = self.client.new_rule(condition=condition, conseq=conseq)
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        data = self.client.get_rule(rule_id)
        self.assertEqual(len(data['actions']), 3)
        self.assertEqual(data['actions'][0]['set-proxy-header'],
                         {'header': 'Foo', 'value': 'default'})
        self.assertEqual(data['actions'][1]['set-proxy-header'],
                         {'header': 'Host', 'value': 'orig'})
        self.assertEqual(data['actions'][2]['print'], {'msg': 'hello'})

        ok = self.client.del_rule(rule_id)
        self.assertTrue(ok)

    def test_global_action(self):
        name = 'action_' + self.apex
        condition = [
            {'var': 'req-method', 'vals': ['GET', 'POST', 'HEAD']}
        ]
        conseq = [
            {
                'exit': {'code': 403}
            }
        ]
        action_id = self.client.new_global_action(name=name,
                                                  condition=condition,
                                                  conseq=conseq)
        self.assertIs(type(action_id), int)
        self.assertGreater(action_id, 0)

        data = self.client.get_global_action(action_id)
        self.assertEqual(data['conditions'][0]['variable'],
                         {'name': 'req-method'})
        self.assertEqual(data['conditions'][0]['values'][0]['val'], 'GET')
        self.assertEqual(data['conditions'][0]['values'][1]['val'], 'POST')
        self.assertEqual(data['conditions'][0]['values'][2]['val'], 'HEAD')
        self.assertEqual(data['actions'][0]['exit'], {'code': 403})

        conseq = [
            {'exit': {'code': 404}}
        ]
        ok = self.client.put_global_action(name=name, action_id=action_id,
                                           condition=condition,
                                           conseq=conseq)
        self.assertTrue(ok)

        data = self.client.get_global_action(action_id)
        self.assertEqual(data['actions'][0]['exit'], {'code': 404})

        conseq = [
            {
                'global_action': action_id
            }
        ]
        rule_id = self.client.new_rule(conseq=conseq, top=1)
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        data = self.client.get_rule(rule_id)
        self.assertEqual(data['actions'][0]['global_action_id'], action_id)

        ok = self.client.del_rule(rule_id)
        self.assertTrue(ok)

        data = self.client.get_all_global_actions()
        self.assertEqual(data[0]['name'], name)

        ok = self.client.del_global_action(action_id)
        self.assertTrue(ok)

        data = self.client.get_global_action(action_id)
        self.assertEqual(data, {})

    def test_get_all_global_waf_rules(self):
        data = self.client.get_all_global_waf_rules()
        for rule in data:
            rule_id = rule['id']
            if rule_id > 10000:
                self.client.del_global_waf_rule(rule_id)

        waf_rule_foo_id = self.client.new_global_waf_rule(
            name='foo',
            code='''uri-arg('foo') =>
    waf-mark-risk(level: 'definite', msg: 'found foo');''')
        self.assertIs(type(waf_rule_foo_id), int)
        self.assertGreater(waf_rule_foo_id, 0)

        waf_rule_bar_id = self.client.new_global_waf_rule(
            name='bar',
            code='''uri-arg('bar') =>
    waf-mark-risk(level: 'definite', msg: 'found bar');''')
        self.assertIs(type(waf_rule_bar_id), int)
        self.assertGreater(waf_rule_bar_id, 0)

        data = self.client.get_all_global_waf_rules(detail=True)
        self.assertEqual(len(data), 14)

        self.assertEqual(data[-1]['name'], 'bar')
        self.assertEqual(data[-1]['code'], '''uri-arg('bar') =>
    waf-mark-risk(level: 'definite', msg: 'found bar');''')
        self.assertEqual(data[-2]['name'], 'foo')
        self.assertEqual(data[-2]['code'], '''uri-arg('foo') =>
    waf-mark-risk(level: 'definite', msg: 'found foo');''')

        data = self.client.get_all_global_waf_rules()

        self.assertEqual(len(data), 14)

        self.assertEqual(data[-1]['name'], 'bar')
        self.assertEqual(data[-1].get('code', None), None)
        self.assertEqual(data[-2]['name'], 'foo')
        self.assertEqual(data[-2].get('code', None), None)

        ok = self.client.del_global_waf_rule(waf_rule_foo_id)
        self.assertTrue(ok)

        ok = self.client.del_global_waf_rule(waf_rule_bar_id)
        self.assertTrue(ok)

        data = self.client.get_all_global_waf_rules()
        self.assertEqual(len(data), 12)

    def test_global_cert_adn_app_cert(self):
        key_file = os.path.join(CURPATH, 'tests', 'test.key')
        cert_file = os.path.join(CURPATH, 'tests', 'test.crt')
        with open(key_file) as f:
            key = f.read()
        with open(cert_file) as f:
            cert = f.read()

        global_cert_id = self.client.set_global_cert_key(key=key, cert=cert)

        data = self.client.get_global_cert_key(global_cert_id)
        self.assertEqual(data['domains'][0], 'test.com')

        new_app_id = self.client.new_app(domains=['test.com'], label='test')
        self.assertIs(type(new_app_id), int)
        self.assertGreater(new_app_id, 0)

        cert_id = self.client.set_cert_key(global_cert_id=global_cert_id)
        self.assertIs(type(cert_id), int)
        self.assertGreater(cert_id, 0)

        ok = self.client.del_cert_key(cert_id)
        self.assertTrue(ok)

        ok = self.client.del_global_cert_key(global_cert_id)
        self.assertTrue(ok)

        data = self.client.get_global_cert_key(global_cert_id)
        self.assertEqual(data, {})

        ok = self.client.del_app(new_app_id)
        self.assertTrue(ok)

        self.client.use_app(self.app_id)

    def test_static_file(self):
        data = self.client.get_all_static_files()
        for file in data:
            file_id = file['id']
            self.client.del_static_file(file_id)

        file_id = self.client.upload_static_file(
            content='content', label='500.html')
        self.assertIs(type(file_id), int)
        self.assertGreater(file_id, 0)

        data = self.client.get_static_file(file_id)
        self.assertEqual(data['label'], '500.html')
        self.assertEqual(data['type'], 'html')
        self.assertEqual(data['id'], file_id)

        condition = [{'var': 'uri', 'op': 'eq', 'val': '/test'}]
        conseq = {
            'set-error-page': {
                'status': [500, 501, 502],
                'content_type': 'text/html; charset=utf8',
                'file_id': file_id
            }
        }
        rule_id = self.client.new_rule(condition=condition, conseq=conseq)
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        data = self.client.get_rule(rule_id)
        self.assertEqual(data['actions'][0]['set-error-page']['status'],
                         [500, 501, 502])
        self.assertEqual(data['actions'][0]['set-error-page']['file_id'],
                         file_id)

        ok = self.client.del_rule(rule_id)
        self.assertTrue(ok)

        new_file_id = self.client.upload_static_file(content='content',
                                                     label='400.html')
        self.assertIs(type(file_id), int)
        self.assertGreater(file_id, 0)

        data = self.client.get_all_static_files()
        self.assertEqual(data[0]['label'], '500.html')
        self.assertEqual(data[1]['label'], '400.html')

        ok = self.client.del_static_file(file_id)
        self.assertTrue(ok)
        ok = self.client.del_static_file(new_file_id)
        self.assertTrue(ok)

    def test_global_upstream(self):
        up_id = self.client.new_global_upstream(
            name='origin-upstream',
            servers=[
                {'ip': '172.22.31.1', 'port': 80},
                {'ip': '172.22.31.2', 'port': 80, 'weight': 2}
            ])
        self.assertIs(type(up_id), int)
        self.assertGreater(up_id, 0)

        ok = self.client.put_global_upstream(
            up_id=up_id,
            name='test-upstream',
            servers=[
                {'ip': '172.22.31.1', 'port': 80}
            ])
        self.assertTrue(ok)

        data = self.client.get_global_upstream(up_id)
        self.assertEqual(data['name'], 'test-upstream')
        self.assertEqual(len(data['nodes']), 1)
        self.assertEqual(data['nodes'][0]['ip'], '172.22.31.1')

        data = self.client.get_all_global_upstreams()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'test-upstream')

        ok = self.client.del_global_upstream(up_id)
        self.assertTrue(ok)

        data = self.client.get_global_upstream(up_id)
        self.assertEqual(data, {})

    def test_global_upstream_and_proxy(self):
        up_id = self.client.new_global_upstream(
            name='origin-upstream',
            servers=[
                {'domain': 'test.com', 'port': 80},
                {'ip': '172.22.31.2', 'port': 80, 'weight': 2}
            ])
        self.assertIs(type(up_id), int)
        self.assertGreater(up_id, 0)

        proxy_rule = {
            'upstreams': [{'global_upstream': up_id, 'weight': 2}],
            'retries': 2,
            "retry_condition": ["invalid_header", "http_500"],
            "balancer_algorithm": "hash",
            "balancer_vars": [
                {"name": "uri"},
                {
                    "name": "uri-arg",
                    "args": "foo"
                }
            ]
        }
        rule_id = self.client.new_rule(proxy=proxy_rule, top=1)
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        condition = [
            {'var': 'host', 'val': 'con.' + self.apex},
            {'var': ['req-header', 'Referer'],
             'vals': [[r'foo\d+', 'rx'], 'foo.com']}
        ]
        conseq = {'redirect': {'url': '/cn/2017/', 'code': 302}}

        proxy_rule['upstreams'][0]['weight'] = 3
        ok = self.client.put_rule(
            rule_id=rule_id, condition=condition,
            conseq=conseq, proxy=proxy_rule)
        self.assertTrue(ok)

        proxy_rule['retries'] = -1
        ok = self.client.put_proxy_rule(rule_id=rule_id, proxy=proxy_rule)
        self.assertTrue(ok)

        data = self.client.get_rule(rule_id)
        self.assertEqual(data['actions'][0]['redirect']['url'], '/cn/2017/')
        self.assertEqual(data['proxy']['upstream'][0]['global_cluster'], up_id)
        self.assertEqual(data['proxy']['upstream'][0]['weight'], 3)
        self.assertEqual(data['proxy']['retries'], -1)
        self.assertEqual(data['proxy']['retry_condition'],
                         ["invalid_header", "http_500"])
        self.assertEqual(data['proxy']['balancer']['algorithm'], 'hash')
        self.assertEqual(data['proxy']['balancer']['variables'][0]['name'],
                         'uri')
        self.assertEqual(data['proxy']['balancer']['variables'][1]['name'],
                         'uri-arg')
        self.assertEqual(data['proxy']['balancer']['variables'][1]['args'],
                         'foo')

        ok = self.client.del_rule(rule_id)
        self.assertTrue(ok)

        data = self.client.get_rule(rule_id)
        self.assertEqual(data, {})

        ok = self.client.del_global_upstream(up_id)
        self.assertTrue(ok)

        data = self.client.get_global_upstream(up_id)
        self.assertEqual(data, {})

    def test_waf_whitelist(self):
        condition = [
            {'var': 'host', 'val': 'con.' + self.apex},
            {'var': ['req-header', 'Referer'],
             'vals': [[r'foo\d+', 'rx'], 'foo.com']}
        ]

        waf_id = self.client.new_waf_whitelist(condition=condition,
                                               rule_sets=[7,8,9,10,11,12,13,14,15,16,17])
        self.assertIs(type(waf_id), int)
        self.assertGreater(waf_id, 0)

        data = self.client.get_waf_whitelist(waf_id)
        self.assertEqual(data['rule_sets'], [7,8,9,10,11,12,13,14,15,16,17])
        self.assertEqual(data['conditions'][0]['variable']['name'], 'host')

        condition = [{
            'var': 'uri',
            'op': '!contains',
            'vals': [
                ['/123.$', 'rx'],
                ['3333ter/', 'rx']
            ]
        }]
        ok = self.client.put_waf_whitelist(whitelist_id=waf_id,
                                           condition=condition,
                                           rule_sets=[7,8,9,10,11,12,13,14,15,16,17])
        self.assertTrue(ok)
        data = self.client.get_waf_whitelist(waf_id)
        self.assertEqual(data['rule_sets'], [7,8,9,10,11,12,13,14,15,16,17])

        data = self.client.get_all_waf_whitelists()
        self.assertEqual(len(data), 1)
        data = data[0]
        self.assertEqual(data['rule_sets'], [7,8,9,10,11,12,13,14,15,16,17])

        ok = self.client.del_waf_whitelist(waf_id)
        self.assertTrue(ok)
        data = self.client.get_all_waf_whitelists()
        self.assertEqual(data, [])
