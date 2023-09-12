# -*- coding: utf-8 -*-
# import io
import sdk_test


class TestEdge(sdk_test.TestSdk):
    def test_dns(self):
        authority = [
            {'domain': 'ns1.' + self.apex, 'ttl': '2 hour'},
            {'domain': 'ns2.' + self.apex, 'ttl': '1 day'}
        ]
        soa_email = 'admin.' + self.apex

        dns_id = self.client.new_dns_app(authority=authority,
                                         soa_email=soa_email, zone=self.apex)
        self.assertIs(type(dns_id), int)
        self.assertGreater(dns_id, 0)

        data = self.client.get_dns_app(dns_id)
        self.assertEqual(data['zone'], self.apex)
        self.assertEqual(data['soa_email'], soa_email)
        self.assertEqual(data['nameserver'][0]['domain'], 'ns1.' + self.apex)
        self.assertEqual(data['nameserver'][0]['unit'], 'hour')
        self.assertEqual(data['nameserver'][0]['ttl'], 2)

        authority = [
            {'domain': 'ns1.' + self.apex, 'ttl': '4 day'},
            {'domain': 'ns2.' + self.apex, 'ttl': '1 day'}
        ]
        ok = self.client.put_dns_app(authority=authority, soa_email=soa_email,
                                     zone=self.apex)
        self.assertTrue(ok)

        data = self.client.get_dns_app(dns_id)
        self.assertEqual(data['nameserver'][0]['unit'], 'day')
        self.assertEqual(data['nameserver'][0]['ttl'], 4)

        ok = self.client.del_dns_app(dns_id)
        self.assertTrue(ok)

        data = self.client.get_dns_app(dns_id)
        self.assertEqual(data, {})

    def test_dns_record(self):
        authority = [
            {'domain': 'ns1.' + self.apex, 'ttl': '2 hour'},
            {'domain': 'ns2.' + self.apex, 'ttl': '1 day'}
        ]
        soa_email = 'admin.' + self.apex

        dns_id = self.client.new_dns_app(authority=authority,
                                         soa_email=soa_email, zone=self.apex)
        self.assertIs(type(dns_id), int)
        self.assertGreater(dns_id, 0)

        record_id = self.client.new_dns_record(sub_domain='bar',
                                               record_type='TXT',
                                               text='text string')
        self.assertIs(type(record_id), int)
        self.assertGreater(record_id, 0)

        ok = self.client.put_dns_record(record_id=record_id,
                                        sub_domain='a.bar',
                                        record_type='TXT',
                                        text='text string')
        self.assertTrue(ok)

        data = self.client.get_dns_record(record_id=record_id)
        self.assertEqual(data['text'], 'text string')
        self.assertEqual(data['sub_domain'], 'a.bar')

        ok = self.client.del_dns_record(record_id=record_id)
        self.assertTrue(ok)

        self.client.new_dns_record(
            ip='127.0.0.1', sub_domain='a', cidr= '127.0.0.1/24',
            record_type='A', ttl='1 hour')

        gateways = self.client.get_all_gateway()
        if len(gateways) > 0:
            gateway_id = gateways[0]['id']
            record_id = self.client.new_dns_record(
                gateway=gateway_id, sub_domain='a', cidr= '127.0.0.1/24',
                record_type='A', ttl='1 hour')

            data = self.client.get_dns_record(record_id=record_id)
            self.assertEqual(data['gateway'], gateway_id)

        try:
            self.client.new_dns_record(
                ip='127.0.0.1', gateway=1, sub_domain='a', cidr= '127.0.0.1/24',
                record_type='A', ttl='1 hour')
        except Exception as e:
            self.assertEqual(e.args[0], 'cannot use ip and gateway at the same time')

        self.client.new_dns_record(
            domain='aspmx.l.google.com', sub_domain='b',
            record_type='CNAME', ttl='1 hour')

        self.client.new_dns_record(
            domain='aspmx.l.google.com', sub_domain='c',
            record_type='MX', priority=3, line=3)

        self.client.new_dns_record(
            text='aspmx.l.google.com', sub_domain='d',
            record_type='TXT', priority=1, ttl='1 hour')

        self.client.new_dns_record(
            text='0 issue "google.com"', sub_domain='d',
            record_type='CAA', priority=1, ttl='1 hour')

        record_id = self.client.new_dns_record(
            domain='aspmx.l.google.com', sub_domain='www',
            record_type='MX', priority=1, ttl='1 hour')
        self.assertIs(type(record_id), int)
        self.assertGreater(record_id, 0)

        ok = self.client.put_dns_record(
            record_id=record_id, domain='aspmx.l.google.com',
            sub_domain='www', record_type='MX', priority=2, ttl='2 hour')
        self.assertTrue(ok)

        data = self.client.get_dns_record(record_id=record_id)
        self.assertEqual(data['priority'], 2)
        self.assertEqual(data['sub_domain'], 'www')

        ok = self.client.del_dns_record(record_id=record_id)
        self.assertTrue(ok)

        data = self.client.get_dns_record(record_id=record_id)
        self.assertEqual(data, {})

    def test_batch_add_dns_app(self):
        soa_email = 'admin@foo.com'
        zones = ["a.com", "b.com"]
        authority = [
            {'domain': 'ns1.foo.com', 'ttl': '2 hour'},
            {'domain': 'ns2.foo.com', 'ttl': '1 day'}
        ]
        for zone in zones:
            dns_id = self.client.new_dns_app(
                authority=authority,
                zone=zone)

            self.client.use_dns_app(dns_id)
            self.client.new_dns_record(sub_domain='@', record_type='A', ip='127.0.0.1')
            self.client.del_dns_app(dns_id)
