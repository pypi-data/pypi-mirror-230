# -*- coding: utf-8 -*-
# import io
import os
import string
import random
import sdk_test


CURPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


class TestVar(sdk_test.TestSdk):
    def test_user_var(self):
        random_name = ''.join([random.choice(string.ascii_letters)
                               for n in range(10)])
        name = 'match-rewrite-' + random_name
        var_id = self.client.new_user_var(name=name, var_type='bool',
                                          default='false')
        self.assertIs(type(var_id), int)
        self.assertGreater(var_id, 0)

        condition = [
            {'user_var': var_id, 'vals': ['true']}
        ]
        conseq = [
            {
                'limit-req-rate':
                {
                    'limit_key': 'uri', 'rate_shape': 1,
                    'rate_reject': 1, 'rate_shape_unit': 'r/min',
                    'rate_reject_unit': 'r/min'
                }
            },
            {'set-var': {'var_id': var_id, 'value': 'false'}}]

        rule_id = self.client.new_rule(condition=condition, conseq=conseq)
        self.assertIs(type(rule_id), int)
        self.assertGreater(rule_id, 0)

        ok = self.client.put_user_var(var_id=var_id, name=name,
                                      var_type='bool', default='true')
        self.assertTrue(ok)

        data = self.client.get_user_var(var_id)
        self.assertEqual(data['default'], 'true')
        self.assertEqual(data['name'], name)

        ok = self.client.del_rule(rule_id)
        self.assertTrue(ok)

        ok = self.client.del_user_var(var_id)
        self.assertTrue(ok)
