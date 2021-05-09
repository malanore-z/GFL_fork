import abc
import os

import torch

from gfl.conf.node import GflNode
from gfl.core.context import WorkDirContext
from gfl.core.data import Job
from gfl.core.data.config import TrainConfig, DatasetConfig
from gfl.core.lfs.path import JobPath
from gfl.net.standlone.send import StandaloneSend
from gfl.utils import TimeUtils, PathUtils


class Trainer(object):

    def __init__(self, job: Job, step: int, client: GflNode = GflNode.default_node):
        super(Trainer, self).__init__()
        self.job_start_time = TimeUtils.millis_time()
        self.job = job
        self.step = step
        self.client = client
        self.round = job.cur_round
        self.job_id = job.job_id
        self.model = None
        self.optimizer = None
        self.lr_scheduler = None
        self.loss = None
        self.epoch = None
        self.batch_size = None
        self.dataset = None
        self.val_dataset = None
        self._parse_train_config(job.train_config)
        self._parse_dataset_config(job.dataset.dataset_config)

    def train(self):
        job_path = JobPath(self.job_id)
        work_dir = job_path.client_work_dir(self.step, self.client.address)
        os.makedirs(work_dir, exist_ok=True)
        with WorkDirContext(work_dir):
            self._pre_train()
            self._train()
            self._post_train()
        # 完成指定轮次的训练之后保存当前模型的训练状态
        StandaloneSend.send_partial_params(self.client.address, self.job_id, self.round, self.model.state_dict())

    def validate(self):
        job_path = JobPath(self.job_id)
        work_dir = job_path.client_work_dir(self.step, self.client.address)
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

    @abc.abstractmethod
    def _split_dataset(self, dataset, rate):
        raise NotImplementedError("")

    def _pre_train(self):
        pass

    @abc.abstractmethod
    def _train(self):
        raise NotImplementedError("")

    def _post_train(self):
        pass

    @abc.abstractmethod
    def _validate(self):
        raise NotImplementedError("")
