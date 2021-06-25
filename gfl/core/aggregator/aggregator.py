import abc
import os
import pickle
import sys
from collections import OrderedDict

import torch
from torch.utils.data import DataLoader

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
        self.dataset = job.dataset.dataset_config.get_dataset()
        self.global_model = None
        self.global_model_weights = None
        self.start_time = TimeUtils.millis_time()
        self.job = job
        self.job_id = job.job_id
        self.step = 0
        self.available_clients = set()
        self.selected_clients = []
        self.clients = set()
        self.global_report = dict()
        self.reports = dict()
        self.should_stop = False
        # 用于获取拓扑结构中的邻居
        self.topology_manager = None
        self._parse_aggregate_config(job.aggregate_config)
        self.init_global_model()

    def run(self):
        self.receive_reports()
        self.choose_clients()
        self.aggregate()
        self.evaluate()
        self.check_should_stop()
        self.step += 1
        self.available_clients = set()
        NetBroadcast.broadcast(self.job_id, self.step, self.global_model_weights, self.job_id)

    def init_global_model(self):
        model = self.job.train_config.get_model()
        model_weights = model.state_dict()
        self.global_model_weights = model_weights
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

    def receive_reports(self):
        """
        获取并且更新当前节点的clients的reports,直接保存到self.reports中
        Returns
        -------

        """
        for client_addr in self.clients:
            client_report = NetReceive.receive(client_addr, self.job_id, self.step, "report")
            self.reports[client_addr] = client_report

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
        self.batch_size = self.job.aggregate_config.get_batch_size()
        self.clients_per_round = aggregate_config.clients_per_round
        self.target_round = aggregate_config.get_round()
        self.loss = aggregate_config.get_loss()

    def compute_weight_updates(self, weights_received):
        baseline_weights = self.global_model_weights
        # Calculate updates from the received weights
        updates = []
        for weight in weights_received:
            update = OrderedDict()
            for name, current_weight in weight.items():
                baseline = baseline_weights[name]
                # Calculate update
                delta = current_weight - baseline
                update[name] = delta
            updates.append(update)
        return updates

    def evaluate(self):
        pass

    def aggregate_evaluate(self):
        pass
