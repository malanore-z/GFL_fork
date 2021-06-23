import numpy as np
from gfl.core.data.config.topology_config import TopologyConfig
from gfl.topology.base_topology_manager import BaseTopologyManager


class CentralizedTopologyManager(BaseTopologyManager):
    """
    中心化的拓扑结构。
    """

    def __init__(self, topology_config: TopologyConfig):
        # 节点总数，中心化的场景下聚合节点只有1个
        self.n = topology_config.get_train_node_num() + 1
        self.train_node_num = topology_config.get_train_node_num()
        # 保存该job的server_address
        self.server_address_list = topology_config.get_client_nodes()
        self.client_address_list = topology_config.get_client_nodes()
        self.topology = topology_config.get_topology()
        # 需要操作这个映射关系的函数,index->node_address。默认0号节点是聚合节点
        self.map = topology_config.get_index2node()
        self.index_num = self.n

    def add_server(self, server_node, add_into_topology: bool):
        self.server_address_list.append(server_node.address)
        if add_into_topology is True:
            self.add_node_into_topology(server_node)

    def add_node_into_topology(self, node, index=-1):
        # 将index->node的映射存入map
        if index == -1:
            self.map[self.index_num] = node.address
            self.index_num += 1
        else:
            self.map[index] = node.address

    def get_index_by_node_address(self, node_address):
        for index, address in self.map.items():
            if address == node_address:
                return index
        return -1

    def generate_topology(self):
        topology_graph = np.zeros([self.n, self.n], dtype=np.float32)
        np.fill_diagonal(topology_graph, 1)
        for i in range(self.n):
            topology_graph[0][i] = 1
        for i in range(self.n):
            topology_graph[i][0] = 1
        self.topology = topology_graph

    def get_in_neighbor_weights(self, node_index):
        if node_index >= self.n:
            return []
        in_neighbor_weights = []
        for row_idx in range(len(self.topology)):
            in_neighbor_weights.append(self.topology[row_idx][node_index])
        return in_neighbor_weights

    def get_out_neighbor_weights(self, node_index):
        if node_index >= self.n:
            return []
        return self.topology[node_index]

    def get_in_neighbor_idx_list(self, node_index):
        neighbor_in_idx_list = []
        neighbor_weights = self.get_in_neighbor_weights(node_index)
        for idx, neighbor_w in enumerate(neighbor_weights):
            if neighbor_w > 0 and node_index != idx:
                neighbor_in_idx_list.append(idx)
        return neighbor_in_idx_list

    def get_out_neighbor_idx_list(self, node_index):
        neighbor_out_idx_list = []
        neighbor_weights = self.get_out_neighbor_weights(node_index)
        for idx, neighbor_w in enumerate(neighbor_weights):
            if neighbor_w > 0 and node_index != idx:
                neighbor_out_idx_list.append(idx)
        return neighbor_out_idx_list

    def get_out_neighbor_node_address_list(self, node_index):
        neighbor_out_node_address_list = []
        neighbor_out_idx_list = self.get_out_neighbor_idx_list(node_index)
        for i in range(len(neighbor_out_idx_list)):
            neighbor_out_node_address_list.append(self.map[neighbor_out_idx_list[i]])
        return neighbor_out_node_address_list

    def get_in_neighbor_node_address_list(self, node_index):
        neighbor_in_node_address_list = []
        neighbor_in_idx_list = self.get_in_neighbor_idx_list(node_index)
        for i in range(len(neighbor_in_idx_list)):
            neighbor_in_node_address_list.append(self.map[neighbor_in_idx_list[i]])
        return neighbor_in_node_address_list
