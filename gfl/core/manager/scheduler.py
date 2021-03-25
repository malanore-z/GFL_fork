import abc
import logging

import torch
import os
from gfl.conf import GflConf
from gfl.conf.node import GflNode
from gfl.core.lfs.path import *
from gfl.core.manager.job_status import *


class JobScheduler(object):

    def __init__(self, *, node, job):
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


class JobAggregateScheduler(JobScheduler):

    def __init__(self, *, node, job):
        super(JobAggregateScheduler, self).__init__(node=node, job=job)

    def start(self):
        pass

    def status(self):
        pass

    def stop(self):
        pass


class JobTrainScheduler(JobScheduler):

    def __init__(self, node, job):
        super(JobTrainScheduler, self).__init__(node=node, job=job)
        # 标识当前任务的状态
        self.__status = JobStatus.JOB_NOT_START

    def start(self):
        """
        启动一轮训练
        """
        # resources_not_already:0
        self.__status = JobStatus.RESOURCE_NOT_ALREADY

        job_id = self.job.job_id
        job_round = self.job.round

        # model_params_path: 保存全局模型参数的路径
        model_params_path = self.get_model_params_path(job_id, job_round)
        if model_params_path is not None:
            # 进行模型训练,并将 模型结果参数 保存
            self.train(model_params_path)
            # epoch_finished: 3
            self.__status = JobStatus.EPOCH_FINISHED

    def status(self):
        """
        返回任务的当前状态
        """
        return self.__status

    def stop(self):
        pass

    def register(self):
        pass

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
        trainer_clazz = self.job.job_config.get_trainer()
        trainer = trainer_clazz(job=self.job, step=self.step, client=self.node)
        # 加载当前的全局模型参数
        trainer.model.load_state_dict(torch.load(model_params_path))
        # trainer._post_train() 需要将训练好的模型进行保存
        trainer.train()

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
        model_params_path = PathUtils.join(global_params_dir, job_id + '.pth')
        # 判断是否存在模型参数文件，如果存在则返回。
        if os.path.exists(global_params_dir) and os.path.isfile(model_params_path):
            # resources_already:1
            self.__status = JobStatus.RESOURCE_ALREADY
            return model_params_path
        else:
            # 等待一段时间。在这段时间内获取到了模型参数文件，则返回
            # 还没写
            # 否则，认为当前模型参数文件已经无法获取
            self.__status = JobStatus.TRAIN_FAILED
            return None
