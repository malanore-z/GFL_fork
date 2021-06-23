import abc
import logging
import os
import pickle
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
from gfl.net.standlone.receive import StandaloneReceive


class JobScheduler(object):

    def __init__(self, *, node: GflNode, job: Job):
        super(JobScheduler, self).__init__()
        self.node = node
        self.job = job
        self.step = 0

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def status(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

    @abc.abstractmethod
    def is_available(self):
        pass

    @abc.abstractmethod
    def is_running(self):
        pass

    @abc.abstractmethod
    def is_finished(self):
        pass


class JobAggregateScheduler(JobScheduler):

    def __init__(self, *, node: GflNode, job, topology_manager):
        super(JobAggregateScheduler, self).__init__(node=node, job=job)
        self.__status = JobStatus.RESOURCE_NOT_ALREADY
        self.__target_round = self.job.aggregate_config.get_round()
        self.job_id = self.job.job_id
        self.topology_manager = topology_manager
        self.aggregator = None
        self.init_aggregator()

    def init_aggregator(self):
        self.job.job_config.aggregator.is_instance = True
        aggregator_clazz = self.job.job_config.get_aggregator()
        self.aggregator = aggregator_clazz(job=self.job)
        self.aggregator.init_topology_manager(self.topology_manager)

    def make_dir(self):
        cur_round = self.job.cur_round
        global_params_path = JobPath(self.job_id).global_params_dir(cur_round)
        os.makedirs(global_params_path, exist_ok=True)

    def start(self):
        """
        启动一轮训练
        Returns
        -------

        """
        # 使用聚合算法对当前收集到的模型进行聚合
        self.make_dir()
        print("开始聚合，轮次：" + str(self.job.cur_round))
        self.aggregate()
        self.job.cur_round += 1
        return self.is_finished()

    def status(self):
        """
        返回任务的当前状态
        """
        return self.__status

    def stop(self):
        pass

    def is_available(self):
        if self.__status == JobStatus.RESOURCE_ALREADY:
            return True
        if self.aggregator.is_available():
            self.__status = JobStatus.RESOURCE_ALREADY
            return True
        else:
            return False

    def is_running(self):
        if self.__status == JobStatus.TRAINING:
            return True
        else:
            return False

    def is_finished(self):
        if self.__status == JobStatus.ALL_FINISHED:
            return True
        else:
            if self.job.cur_round == self.__target_round:
                self.__status = JobStatus.ALL_FINISHED
                return True
            else:
                return False

    def aggregate(self):
        print("Aggregator开始模型聚合")
        self.aggregator.run()
        self.__status = JobStatus.EPOCH_FINISHED


class JobTrainScheduler(JobScheduler):

    def __init__(self, *, node: GflNode, job: Job, topology_manager):
        super(JobTrainScheduler, self).__init__(node=node, job=job)
        self.__status = JobStatus.RESOURCE_NOT_ALREADY
        self.__target_round = self.job.aggregate_config.get_round()
        self.job_id = self.job.job_id
        self.trainer = None
        self.topology_manager = topology_manager
        self.init_trainer()

    def init_trainer(self):
        self.job.job_config.trainer.is_instance = True
        trainer_clazz = self.job.job_config.get_trainer()
        self.trainer = trainer_clazz(job=self.job, step=self.step, client=self.node)
        self.trainer.init_topology_manager(self.topology_manager)

    def make_dir(self):
        cur_round = self.job.cur_round
        client_params_dir = JobPath(self.job_id).client_params_dir(cur_round, self.node.address)
        os.makedirs(client_params_dir, exist_ok=True)

    def start(self):
        """
        启动一轮训练
        """
        # 调用start之前，调用is_available，保证全局模型路径下的模型已经存在
        # 进行模型训练,并将 模型结果参数 保存
        self.make_dir()
        self.train()
        self.job.cur_round += 1
        return self.is_finished()

    def status(self):
        """
        返回任务的当前状态
        """
        return self.__status

    def stop(self):
        pass

    def is_available(self):
        # 判断当前的状态是否为RESOURCE_ALREADY
        if self.__status == JobStatus.RESOURCE_ALREADY:
            return True
        if self.trainer.is_available():
            self.__status = JobStatus.RESOURCE_ALREADY
            return True
        else:
            return False

    def is_running(self):
        if self.__status == JobStatus.TRAINING:
            return True
        else:
            return False

    def is_finished(self):
        if self.__status == JobStatus.ALL_FINISHED:
            return True
        else:
            if self.job.cur_round == self.__target_round:
                self.__status = JobStatus.ALL_FINISHED
                return True
            else:
                return False

    def register(self):
        NetSend.send_cmd_register(self.job.job_id, self.node.address, self.node.pub_key, self.job.dataset.dataset_id)

    def train(self):
        """
        加载模型参数，并训练指定的step，并将训练好的模型参数进行保存
        Parameters
        ----------

        Returns trainer
        -------

        """
        print("Trainer开始训练，轮次：" + str(self.job.cur_round))
        self.__status = JobStatus.TRAINING
        self.trainer.train()
        self.__status = JobStatus.EPOCH_FINISHED
