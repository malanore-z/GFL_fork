import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor

from gfl.core.data.config import TopologyConfig
from gfl.core.lfs.data import save_topology_manager, load_topology_manager
from gfl.conf.node import GflNode
from gfl.node.manager import NodeManager
from gfl.topology.centralized_topology_manager import CentralizedTopologyManager
from gfl_test.job.generate_job import generate_job


class TestMethod(unittest.TestCase):
    def setUp(self) -> None:
        # GflNode.init_node()
        GflNode.load_node()
        node_server = GflNode.standalone_nodes[0]
        node_client1 = GflNode.standalone_nodes[1]
        node_client2 = GflNode.standalone_nodes[2]
        self.node_manager_server = NodeManager(node=node_server, role="server")
        self.node_manager_client1 = NodeManager(node=node_client1, role="client")
        self.node_manager_client2 = NodeManager(node=node_client2, role="client")
        # 创建job
        self.job = generate_job()
        # 创建job对应的拓扑
        topology_config = TopologyConfig()
        topology_config.with_train_node_num(2)
        topology_config.with_server_nodes([node_server.address])
        topology_config.with_client_nodes([node_client1.address, node_client2.address])
        topology_config.with_index2node([node_server.address, node_client1.address, node_client2.address])
        temp_topology_manager = CentralizedTopologyManager(topology_config)
        temp_topology_manager.generate_topology()
        # 保存job对应的拓扑
        save_topology_manager(job_id=self.job.job_id, topology_manager=temp_topology_manager)

    def test_process(self):
        # threads = []
        # t1 = threading.Thread(target=self.node_manager_server.run)
        # threads.append(t1)
        # t2 = threading.Thread(target=self.node_manager_client1.run)
        # threads.append(t2)
        # t3 = threading.Thread(target=self.node_manager_client2.run)
        # threads.append(t3)
        #
        # for t in threads:
        #     t.setDaemon(True)
        #     t.start()
        #     print("******************")
        #     time.sleep(1)
        # for t in threads:
        #     t.join()

        with ThreadPoolExecutor(max_workers=3) as t:
            task1 = t.submit(self.node_manager_server.run)
            task2 = t.submit(self.node_manager_client1.run)  # 通过submit提交执行的函数到线程池中
            task3 = t.submit(self.node_manager_client2.run)


if __name__ == '__main__':
    unittest.main()
