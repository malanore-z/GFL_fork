import unittest

from gfl.conf.node import GflNode
from gfl_test.job.generate_job import generate_job, generate_dataset
from gfl.topology.decentralized_topology_manager import DeCentralizedTopologyManager


class TestMethod(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_start(self):
        # 生成dataset和job
        self.dataset = generate_dataset()
        print("生成的dataset_id:" + self.dataset.dataset_id)
        self.job = generate_job()
        print("生成的job_id:" + self.job.job_id)
        self.job.mount_dataset(self.dataset)

        self.tpmgr = DeCentralizedTopologyManager(n=6, job=self.job, neighbor_num=2)

        GflNode.init_node()
        node1 = GflNode.default_node
        self.tpmgr.add_node_into_topology(node1)

        GflNode.init_node()
        node2 = GflNode.default_node
        self.tpmgr.add_node_into_topology(node2)

        GflNode.init_node()
        node3 = GflNode.default_node
        self.tpmgr.add_node_into_topology(node3)

        GflNode.init_node()
        node4 = GflNode.default_node
        self.tpmgr.add_node_into_topology(node4)

        GflNode.init_node()
        node5 = GflNode.default_node
        self.tpmgr.add_node_into_topology(node5)

        GflNode.init_node()
        node6 = GflNode.default_node
        self.tpmgr.add_node_into_topology(node6)

        self.tpmgr.generate_topology()
        print("tpmgr.topology = " + str(self.tpmgr.topology))
        print("tpmgr.job_id = " + str(self.tpmgr.job_id))

        # get the OUT neighbor weights for node 0
        out_neighbor_weights = self.tpmgr.get_out_neighbor_weights(0)
        print("out_neighbor_weights = " + str(out_neighbor_weights))

        # get the OUT neighbor index list for node 0
        out_neighbor_idx_list = self.tpmgr.get_out_neighbor_idx_list(0)
        print("out_neighbor_idx_list = " + str(out_neighbor_idx_list))

        neighbor_out_node_list = self.tpmgr.get_out_neighbor_node_list(0)
        print("out_neighbor_node_list = " + str(neighbor_out_node_list))

        # get the IN neighbor weights for node 0
        in_neighbor_weights = self.tpmgr.get_in_neighbor_weights(0)
        print("in_neighbor_weights = " + str(in_neighbor_weights))

        # get the IN neighbor index list for node 0
        in_neighbor_idx_list = self.tpmgr.get_in_neighbor_idx_list(0)
        print("in_neighbor_idx_list = " + str(in_neighbor_idx_list))

        neighbor_in_node_list = self.tpmgr.get_in_neighbor_node_list(0)
        print("in_neighbor_node_list = " + str(neighbor_in_node_list))
        # for i in len(neighbor_in_node_list):
        for neighbor in neighbor_in_node_list:
            print(neighbor.address)



if __name__ == "__main__":
    unittest.main()
