# -*- coding: utf-8 -*-
# import io
import os
import random
import sdk_test


CURPATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


class TestRule(sdk_test.TestSdk):
    def test_rule_reorder(self):
        condition = [{'var': 'uri', 'op': 'eq', 'val': '/favicon.ico'}]
        conseq = [
            {'print': {
                'msg': 'hello'
            }}
        ]
        rule_id1 = self.client.new_rule(condition=condition, conseq=conseq, order=1)
        self.assertIs(type(rule_id1), int)
        self.assertGreater(rule_id1, 0)

        rule_id2 = self.client.new_rule(condition=condition, conseq=conseq, order=2)
        self.assertIs(type(rule_id2), int)
        self.assertGreater(rule_id2, 0)

        rule2 = self.client.get_rule(rule_id2)
        self.assertIs(type(rule2['order']), int)

        rule2_order = rule2['order']
        # insert rule after rule1, before rule 2
        rule_id3 = self.client.new_rule(condition=condition, conseq=conseq,
            order=rule2_order, reorder=True)
        self.assertIs(type(rule_id3), int)
        self.assertGreater(rule_id3, 0)

        # check rule2 order, it should have a new order
        rule2 = self.client.get_rule(rule_id2)
        self.assertEqual(rule2['order'], rule2_order + 1)

        # get rule3
        rule3 = self.client.get_rule(rule_id3)
        self.assertEqual(rule3['order'], rule2_order)

        # insert rule without reorder
        rule_id4 = self.client.new_rule(condition=condition, conseq=conseq,
            order=rule2_order)
        self.assertIs(type(rule_id3), int)
        self.assertGreater(rule_id3, 0)

        # get rule4
        rule4 = self.client.get_rule(rule_id3)
        self.assertEqual(rule4['order'], rule2_order)

        rules = self.client.get_all_rules()
        self.assertNotEqual(rule4['order'], rules[0]['order'])
        self.assertEqual(rule4['order'], rules[1]['order'])
        self.assertEqual(rule4['order'], rules[2]['order'])

        ok = self.client.del_rule(rule_id1)
        ok = self.client.del_rule(rule_id2)
        ok = self.client.del_rule(rule_id3)
        ok = self.client.del_rule(rule_id4)

        self.assertTrue(ok)
