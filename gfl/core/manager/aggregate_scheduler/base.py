import abc
import logging
import os
import pickle
import sys
from typing import List

import torch
import os
from gfl.conf import GflConf
from gfl.conf.node import GflNode
from gfl.core.data.job import Job
from gfl.net import NetSend, NetFetch, NetReceive, NetBroadcast
from gfl.core.lfs.path import *
from gfl.core.manager.job_status import *
from gfl.core.trainer import SupervisedTrainer
from gfl.net.standlone.receive import StandaloneReceive
from gfl.net.standlone.broadcast import StandaloneBroadcast
from gfl.core.lfs.path import JobPath
from gfl.core.manager.sql_execute import *
from gfl.core.manager.scheduler import JobScheduler


class AggregateScheduler(JobScheduler):

    def __init__(self, *, node: GflNode, job):
        super(AggregateScheduler, self).__init__(node=node, job=job)
        self.client = None
        self.clients = {}
        self.total_clients = 0
        self.selected_clients = None
        self.clients_per_round = job.aggregate_config.clients_per_round
        self.accuracy = 0
        self.client_model_params = {}
        self.reports = []
        self.__status = JobStatus.RESOURCE_NOT_ALREADY
        self.__target_round = self.job.aggregate_config.get_round()

    def start(self, client=None):
        # 生成一个初始的全局模型
        if self.step == 0:
            self.init_global_model()
        self.client = client
        self.configure()

        print(f"Starting a aggregate_scheduler at address {self.node.address}")

    def init_global_model(self):
        job_id = self.job.job_id
        path_util = JobPath(self.job.job_id)
        global_model_path = path_util.global_params_dir(0)
        os.makedirs(global_model_path, exist_ok=True)
        global_model_path += f"/{job_id}.pth"
        torch.save(self.job.train_config.get_model().state_dict(), global_model_path)

    def check_stop(self):
        if self.step >= self.__target_round:
            print("Target number of training rounds reached.")
        self.stop()

    def stop(self):
        """停止训练"""
        pass

    def select_clients(self):
        """选择部分client并发送信息让他们开始训练"""
        # 清空上一轮的训练结果
        self.reports = []
        self.step += 1

        print(f"[Job {self.job.job_id}] Starting round {self.step}")

        # 由子类实现client的选择逻辑
        self.choose_clients()

        if len(self.selected_clients) > 0:
            pass

    def send(self, data, name, client_addr):
        """send data to target client"""
        print(f"[Job {self.job.job_id}] Aggregator broadcasting {name} to client {client_addr}")
        pickled_data = pickle.dumps(data)
        data_size = sys.getsizeof(pickled_data)
        path_util = JobPath(self.job.job_id)
        client_path = path_util.client_params_dir(self.step, client_addr)
        os.makedirs(client_path, exist_ok=True)
        data_path = client_path + f"/{name}.pkl"
        with open(data_path) as f:
            pickle.dump(pickled_data, f)
        print(
            f"[Job {self.job.job_id}] Aggregator send {round(data_size / 1024 ** 2, 2)} MB of {name} data to client {client_addr}")

    def broadcast(self, data, name, clients=None):
        """broadcast message to all selected clients"""
        print(f"[Job {self.job.job_id}] Aggregator broadcasting {name} to clients")
        pickled_data = pickle.dumps(data)
        data_size = sys.getsizeof(pickled_data)
        path_util = JobPath(self.job.job_id)
        global_path = path_util.global_params_dir(self.step)
        os.makedirs(global_path, exist_ok=True)
        data_path = global_path + f"/{name}.pkl"
        with open(data_path) as f:
            pickle.dump(pickled_data, f)

        print(f"[Job {self.job.job_id}] Aggregator send {round(data_size / 1024**2, 2)} MB of {name} data to all selected clients")

    @abc.abstractmethod
    def configure(self):
        """配置相关参数"""

    @abc.abstractmethod
    def choose_clients(self):
        """选择部分client来参与模型的聚合"""