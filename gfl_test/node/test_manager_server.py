from gfl.core.data.config import TopologyConfig
from gfl.core.lfs.data import save_topology_manager
from gfl.conf.node import GflNode
from gfl.node.manager import NodeManager
from gfl.topology.centralized_topology_manager import CentralizedTopologyManager
from gfl_test.job.generate_job import generate_job

if __name__ == '__main__':
    # GflNode.init_node()
    GflNode.load_node()
    node_server = GflNode.standalone_nodes[0]
    node_client1 = GflNode.standalone_nodes[1]
    node_client2 = GflNode.standalone_nodes[2]
    node_manager_server = NodeManager(node=node_server, role="server")
    # self.node_manager_client1 = NodeManager(node=node_client1, role="client")
    # self.node_manager_client2 = NodeManager(node=node_client2, role="client")
    # 创建job
    job = generate_job()

    # 创建job对应的拓扑并保存
    topology_config = TopologyConfig()
    topology_config.with_train_node_num(2)
    topology_config.with_server_nodes([node_server.address])
    topology_config.with_client_nodes([node_client1.address, node_client2.address])
    topology_config.with_index2node([node_server.address, node_client1.address, node_client2.address])
    temp_topology_manager = CentralizedTopologyManager(topology_config)
    temp_topology_manager.generate_topology()
    save_topology_manager(job_id=job.job_id, topology_manager=temp_topology_manager)
    node_manager_server.run()
