import abc
import os
import pickle
import sys

import torch

from gfl.conf.node import GflNode
from gfl.core.context import WorkDirContext
from gfl.core.data import Job
from gfl.core.data.config import AggregateConfig
from gfl.core.lfs.path import JobPath
from gfl.utils import TimeUtils, PathUtils
from gfl.net.standlone import *


class Aggregator(object):

    def __init__(self, job: Job, server: GflNode = GflNode.default_node):
        super(Aggregator, self).__init__()
        self.global_model = None
        self.start_time = TimeUtils.millis_time()
        self.job = job
        self.job_id = job.job_id
        self.step = 0
        self.clients_per_round = self.job.aggregate_config.clients_per_round
        self.target_round = self.job.aggregate_config.get_round()
        self.available_clients = set()
        self.selected_clients = []
        self.clients = set()
        self.should_stop = False
        # 用于获取拓扑结构中的邻居
        self.topology_manager = None
        self._parse_aggregate_config(job.aggregate_config)
        self.init_global_model()

    def run(self):
        self.choose_clients()
        self.aggregate()
        self.check_should_stop()
        self.step += 1
        self.available_clients = set()
        NetBroadcast.broadcast(self.job_id, self.step, self.global_model, self.job_id)

    def init_global_model(self):
        model = self.job.train_config.get_model()
        model_weights = model.state_dict()
        self.broadcast(model_weights, self.job_id)

    def init_topology_manager(self, topology_manager):
        self.topology_manager = topology_manager

    def update_clients(self):
        """
        获取并且更新当前节点的client的地址
        Returns
        -------

        """
        # 这边还需要判断是否在client是否存在于neighbor_in_node_list = self.tpmgr.get_in_neighbor_node_list(0)
        # 获取聚合方在拓扑结构当中的邻居节点，在中心化的情况下，默认聚合节点的序号是0，
        neighbor_in_node_address_list = self.topology_manager.get_in_neighbor_node_address_list(0)
        client = NetReceive.receive_cmd_register(self.job.job_id)
        while client is not None:
            for neighbor_address in neighbor_in_node_address_list:
                if client['address'] == neighbor_address:
                    self.clients.add(client['address'])
            client = NetReceive.receive_cmd_register(self.job.job_id)

    def update_clients_models(self):
        """
        获取并且更新当前节点的clients的模型（仅保存其路径，不加载模型)
        Returns
        -------

        """
        for client_addr in self.clients:
            client_params_dir = JobPath(self.job_id).client_params_dir(self.step, client_addr) + f"/{self.job_id}.pth"
            if os.path.exists(client_params_dir):
                self.client_models[client_addr] = client_params_dir

    def is_available(self):
        # 获取模型前先更新客户端
        self.update_clients()
        n_available_models = 0
        for client_addr in self.clients:
            client_params_dir = JobPath(self.job_id).client_params_dir(self.step, client_addr) + f"/{self.job_id}.pkl"
            if os.path.exists(client_params_dir):
                n_available_models += 1
                self.available_clients.add(client_addr)
        if n_available_models >= self.job.aggregate_config.clients_per_round:
            return True
        else:
            return False

    def check_should_stop(self):
        """
        判断是否需要停止训练
        Returns
        -------

        """
        if self.step >= self.target_round:
            self.should_stop = True

    def send(self, client_address, name, data):
        """
        发送数据给指定的client
        Parameters
        ----------
        client_address: 指定client的地址
        name: 数据的命名(用于标识数据)
        data: 需要发送的数据

        Returns
        -------

        """
        NetSend.send(client_address, self.job_id, self.step, name, data)

    def broadcast(self, data, name, clients=None):
        """broadcast message to all selected clients"""
        NetBroadcast.broadcast(self.job_id, self.step, data, name)

    def receive(self, client_address, name):
        pass

    @abc.abstractmethod
    def aggregate(self):
        """进行模型的聚合"""

    @abc.abstractmethod
    def choose_clients(self):
        """选取部分模型进行聚合"""

    def _parse_aggregate_config(self, aggregate_config: AggregateConfig):
        pass
