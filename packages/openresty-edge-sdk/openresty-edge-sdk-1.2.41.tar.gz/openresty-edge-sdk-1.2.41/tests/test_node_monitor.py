# -*- coding: utf-8 -*-
# import io
import sdk_test

class TestNodeMonitor(sdk_test.TestSdk):
    def test_node_monitor(self):
        # [{'system_net_packets_sent': 523.14583333333, 'system_CPU_percent': 44.854166666667, 'system_swap_total': 2147479552, 'system_CPU_loadavg_15m': 1.8879166666667, 'system_net_err_in': 0, 'system_CPU_loadavg_5m': 1.9847916666667, 'system_net_packets_recv': 498.85416666667, 'system_net_err_out': 0, 'system_swap_used': 6553600, 'system_CPU_loadavg_1m': 1.58, 'system_net_drop_out': 0, 'system_memory_used': 6050292053.3333, 'system_net_bytes_sent': 241699.75, 'system_memory_total': 12360978432, 'system_CPU_core': 8, 'system_net_drop_in': 0, 'system_net_bytes_recv': 312615.3125, 'node_utime': 1627462187, 'node_id': 1, 'max_id': 2822}]
        gateways = self.client.get_all_gateway()
        # print("gateways = ", gateways)

        for gateway in gateways:
            nodes = gateway.get('nodes', [])
            # print("nodes = ", nodes)
            for node in nodes:
                data = self.client.node_monitor(node['id'])
                self.assertIs(type(data), list)
