import abc
import os
import pickle

import torch

from gfl.conf.node import GflNode
from gfl.core.context import WorkDirContext
from gfl.core.data import Job
from gfl.core.data.config import TrainConfig, DatasetConfig
from gfl.core.lfs.path import JobPath
from gfl.net.standlone.receive import StandaloneReceive
from gfl.net.standlone.send import StandaloneSend
from gfl.utils import TimeUtils, PathUtils


class Trainer(object):

    def __init__(self, job: Job, step: int, client: GflNode = GflNode.default_node):
        super(Trainer, self).__init__()
        self.job_start_time = TimeUtils.millis_time()
        self.job = job
        self.step = step
        self.client = client
        # self.round = job.cur_round
        self.job_id = job.job_id
        self.model = None
        self.optimizer = None
        self.lr_scheduler = None
        self.loss = None
        self.epoch = None
        self.batch_size = None
        self.dataset = None
        self.val_dataset = None
        # 用于获取拓扑结构中的邻居
        self.topology_manager = None
        self._parse_train_config(job.train_config)
        self._parse_dataset_config(job.dataset.dataset_config)
        self.__model_params_path = None
        self.reports = {}

    def init_topology_manager(self, topology_manager):
        self.topology_manager = topology_manager

    def train(self):
        self._pre_train()
        job_path = JobPath(self.job_id)
        work_dir = job_path.client_work_dir(self.job.cur_round, self.client.address)
        os.makedirs(work_dir, exist_ok=True)
        with WorkDirContext(work_dir):
            # self._pre_train()
            self._train()
            self._post_train()
        # 完成指定轮次的训练之后保存当前模型的训练状态
        StandaloneSend.send_partial_params(self.client.address, self.job_id, self.job.cur_round, self.model.state_dict())
        StandaloneSend.send(self.client.address, self.job_id, self.job.cur_round, "report", self.reports)
        # 初始化self.__model_params_path，准备下一轮训练
        self.__model_params_path = None

    def validate(self):
        job_path = JobPath(self.job_id)
        work_dir = job_path.client_work_dir(self.job.cur_round, self.client.address)
        os.makedirs(work_dir, exist_ok=True)
        with WorkDirContext(work_dir):
            self._validate()

    def _parse_train_config(self, train_config: TrainConfig):
        self.model = train_config.get_model()
        self.optimizer = train_config.get_optimizer(self.model)
        self.lr_scheduler = train_config.get_lr_scheduler(self.optimizer)
        self.loss = train_config.get_loss()
        self.epoch = train_config.get_epoch()
        self.batch_size = train_config.get_batch_size()

    def _parse_dataset_config(self, dataset_config: DatasetConfig):
        self.dataset = dataset_config.get_dataset()
        self.val_dataset = dataset_config.get_val_dataset()
        if self.val_dataset is None:
            self.dataset, self.val_dataset = self._split_dataset(self.dataset, dataset_config.get_val_rate())

    def is_available(self):
        # 尝试去获取服务器端的全局模型
        # 获取到则返回True
        # 没有获取到则返回False

        # 获取聚合节点的地址，和neighbor_in_node_list中的neighbor比较
        index_in_topology = self.topology_manager.get_index_by_node(self.client)
        neighbor_in_node_address_list = self.topology_manager.get_in_neighbor_node_address_list(index_in_topology)
        server_address_list = self.topology_manager.server_address_list
        for server_address in server_address_list:
            for neighbor_address in neighbor_in_node_address_list:
                if server_address == neighbor_address:
                    # __model_params_path可能有多个，那需要使用列表才存储
                    self.__model_params_path = StandaloneReceive.receive_global_params(job_id=self.job.job_id,
                                                                                       cur_round=self.job.cur_round)
        # self.__model_params_path = StandaloneReceive.receive_global_params(job_id=self.job.job_id,
        #                                                                    cur_round=self.job.cur_round)
        if self.__model_params_path is None:
            return False
        else:
            return True

    @abc.abstractmethod
    def _split_dataset(self, dataset, rate):
        raise NotImplementedError("")

    def _pre_train(self):
        if self.__model_params_path is not None:
            with open(self.__model_params_path, 'rb') as f:
                self.model.load_state_dict(pickle.load(f))

    @abc.abstractmethod
    def _train(self):
        raise NotImplementedError("")

    def _post_train(self):
        pass

    @abc.abstractmethod
    def _validate(self):
        raise NotImplementedError("")
