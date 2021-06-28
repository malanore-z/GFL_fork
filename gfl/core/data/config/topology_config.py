from typing import List, Dict

from gfl.core.data.config.config import Config


class TopologyConfig(Config):
    train_node_num: int
    server_nodes: List[str]
    client_nodes: List[str]
    topology: List[List[int]]
    index2node: List[str]
    isCentralized: bool

    def with_train_node_num(self, train_node_num):
        self.train_node_num = train_node_num
        return self

    def with_server_nodes(self, server_nodes):
        self.server_nodes = server_nodes
        return self

    def with_client_nodes(self, client_nodes):
        self.client_nodes = client_nodes
        return self

    def with_topology(self, topology):
        self.topology = topology
        return self

    def with_index2node(self, index2node):
        self.index2node = index2node
        return self

    def with_isCentralized(self, isCentralized):
        self.isCentralized = isCentralized
        return self

    def get_train_node_num(self):
        return self.train_node_num

    def get_server_nodes(self):
        return self.server_nodes

    def get_client_nodes(self):
        return self.client_nodes

    def get_topology(self):
        return self.topology

    def get_index2node(self):
        return self.index2node

    def get_isCentralized(self):
        return self.isCentralized
