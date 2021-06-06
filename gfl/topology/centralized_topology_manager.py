import networkx as nx
import numpy as np

from gfl.topology.base_topology_manager import BaseTopologyManager
from gfl.core.data.job import Job


class CentralizedTopologyManager(BaseTopologyManager):
    """
    中心化的拓扑结构。

    Arguments:
        n (int): number of nodes in the topology.
        job (Job): 与该拓扑结构关联的Job
        aggregate_node: the node used to aggregate
    """

    def __init__(self, n, job: Job, aggregate_node=None):
        # 节点总数，聚合节点只有一个
        self.n = n
        self.train_node_num = n - 1
        self.aggregate_node = aggregate_node
        self.topology = []
        self.job_id = job.job_id
        # 需要操作这个映射关系的函数,index->node。默认0号节点是聚合节点
        self.map = {}
        self.index_num = 0
        if self.aggregate_node is not None:
            self.add_node_into_topology(self.aggregate_node)

    def add_node_into_topology(self, node, index=-1):
        # 将index->node的映射存入map
        if index == -1:
            self.map[self.index_num] = node
            self.index_num += 1
        else:
            self.map[index] = node

    def get_index_by_node_address(self, node_address):
        for index, node in self.map.items():
            if node.address == node_address:
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

    def get_out_neighbor_node_list(self, node_index):
        neighbor_out_node_list = []
        neighbor_out_idx_list = self.get_out_neighbor_idx_list(node_index)
        for i in range(len(neighbor_out_idx_list)):
            neighbor_out_node_list.append(self.map[neighbor_out_idx_list[i]])
        return neighbor_out_node_list

    def get_in_neighbor_node_list(self, node_index):
        neighbor_in_node_list = []
        neighbor_in_idx_list = self.get_in_neighbor_idx_list(node_index)
        for i in range(len(neighbor_in_idx_list)):
            neighbor_in_node_list.append(self.map[neighbor_in_idx_list[i]])
        return neighbor_in_node_list
