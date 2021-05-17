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

    def __init__(self, *, node: GflNode, job):
        super(JobAggregateScheduler, self).__init__(node=node, job=job)
        self.__status = JobStatus.RESOURCE_NOT_ALREADY
        self.__target_round = self.job.aggregate_config.get_round()
        self.job_id = self.job.job_id
        self.aggregator = None
        self.init_aggregator()

    def init_aggregator(self):
        self.job.job_config.aggregator.is_instance = True
        aggregator_clazz = self.job.job_config.get_aggregator()
        self.aggregator = aggregator_clazz(job=self.job)

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

    def __init__(self, *, node: GflNode, job: Job):
        super(JobTrainScheduler, self).__init__(node=node, job=job)
        # 标识当前任务的状态
        self.__status = JobStatus.RESOURCE_NOT_ALREADY
        # 全局模型参数的路径
        self.__model_params_path = None
        self.__target_round = self.job.aggregate_config.get_round()

    def start(self):
        """
        启动一轮训练
        """
        # 调用start之前，调用is_available，保证全局模型路径下的模型已经存在
        # 进行模型训练,并将 模型结果参数 保存
        print("训练方开始训练，轮次：" + str(self.job.cur_round))
        self.train(model_params_path=self.__model_params_path)
        self.job.cur_round += 1
        self.is_finished()

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
        else:
            self.__model_params_path = self.get_model_params_path(job_id=self.job.job_id, job_round=self.job.cur_round)

        if self.__model_params_path is None:
            return False
        else:
            return True

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

    def train(self, model_params_path):
        """
        加载模型参数，并训练指定的step，并将训练好的模型参数进行保存
        Parameters
        ----------
        model_params_path: 保存模型参数的路径

        Returns trainer
        -------

        """
        # training: 2
        self.__status = JobStatus.TRAINING
        self.job.job_config.trainer.is_instance = True
        # trainer_clazz : ConfigObject
        trainer_clazz = self.job.job_config.get_trainer()
        trainer = trainer_clazz(job=self.job, step=self.step, client=self.node)
        # 加载当前的全局模型参数
        # trainer.model.load_state_dict(torch.load(model_params_path))
        with open(model_params_path, 'rb') as f:
            trainer.model.load_state_dict(pickle.load(f))
        # trainer._post_train() 需要将训练好的模型进行保存
        trainer.train()
        # epoch_finished: 3
        self.__status = JobStatus.EPOCH_FINISHED

    def get_model_params_path(self, job_id, job_round):
        """
        获取 id 为 job_id 并且训练轮次为 job_round 的全局模型参数的路径。
        若无该路径，说明模型参数还没有准备完成 或 全局模型的聚合已经进行到之后的轮次了。
        Parameters
        ----------
        job_id: job_id
        job_round: 当前这轮训练的轮次

        Returns model_params_path：保存模型参数的路径
        -------
        """
        # 根据 Job 中的 job_id 和 job_round 获取指定轮次聚合后的 全局模型参数的路径
        global_params_dir = JobPath(job_id).global_params_dir(job_round)
        model_params_path = PathUtils.join(global_params_dir, job_id + '.pkl')
        # 判断是否存在模型参数文件，如果存在则返回。
        if os.path.exists(global_params_dir) and os.path.isfile(model_params_path):
            # resources_already:1
            self.__status = JobStatus.RESOURCE_ALREADY
            print("训练方可以调用全局模型")
            return model_params_path
        else:
            # 等待一段时间。在这段时间内获取到了模型参数文件，则返回
            # 暂时不考虑这种情况
            # 否则，认为当前模型参数文件已经无法获取
            self.__status = JobStatus.TRAIN_FAILED
            return None
