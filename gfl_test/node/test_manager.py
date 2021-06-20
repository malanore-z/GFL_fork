import threading
import time
import unittest
import gfl.core.lfs as lfs
from gfl.conf.node import GflNode
from gfl.node.manager import NodeManager
from gfl.topology.centralized_topology_manager import CentralizedTopologyManager
from gfl_test.job.generate_job import generate_job, generate_dataset


class TestMethod(unittest.TestCase):
    def setUp(self) -> None:
        GflNode.init_node()
        node_server = GflNode.default_node
        GflNode.init_node()
        node_client1 = GflNode.default_node
        GflNode.init_node()
        node_client2 = GflNode.default_node
        self.node_manager_server = NodeManager(node=node_server, role="server")
        self.node_manager_client1 = NodeManager(node=node_client1, role="client")
        self.node_manager_client2 = NodeManager(node=node_client2, role="client")
        self.node_manager_client1.server_node = node_server
        self.node_manager_client2.server_node = node_server
        self.job = generate_job()
        self.tpmgr = CentralizedTopologyManager(n=3, job=self.job, aggregate_node=node_server)
        self.tpmgr.add_node_into_topology(node_client1, 1)
        self.tpmgr.add_node_into_topology(node_client2, 2)
        self.node_manager_server.tpmgr = self.tpmgr
        self.node_manager_client1.tpmgr = self.tpmgr
        self.node_manager_client2.tpmgr = self.tpmgr
        self.tpmgr.generate_topology()

    def test_process(self):
        threads = []
        t1 = threading.Thread(target=self.node_manager_server.run)
        threads.append(t1)
        t2 = threading.Thread(target=self.node_manager_client1.run)
        threads.append(t2)
        t3 = threading.Thread(target=self.node_manager_client2.run)
        threads.append(t3)

        for t in threads:
            t.setDaemon(True)
            t.start()
            time.sleep(2)
        for t in threads:
            t.join()

if __name__ == '__main__':
    unittest.main()