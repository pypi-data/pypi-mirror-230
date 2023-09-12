# -*- coding: utf-8 -*-
# import io
import sdk_test


class TestGateWay(sdk_test.TestSdk):
    def test_get_all_gateway(self):
        tags = self.client.get_all_gateway_tag()

        for tag in tags:
            self.client.del_gateway_tag(tag['id'])

        data=self.client.get_all_gateway()

        tag1 = self.client.add_gateway_tag("tag1")
        tag2 = self.client.add_gateway_tag("tag2")

        self.client.del_gateway_tag(tag1)

        gateway1 = self.client.add_gateway("gateway1", 1, [ tag2 ])

        data=self.client.get_all_gateway()
        self.assertEqual(type(data), type(list()))

        self.client.del_gateway(gateway1)
        self.client.del_gateway_tag(tag2)
