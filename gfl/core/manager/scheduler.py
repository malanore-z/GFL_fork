import abc
import logging
import os
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

    def __init__(self, *, node: GflNode, job: Job):
        super(JobAggregateScheduler, self).__init__(node=node, job=job)
        self.client_model_paths = None

    def start(self):
        job_id, cur_round = self.job.job_id, self.job.cur_round
        self.client_model_paths = self.get_client_model_paths(job_id, cur_round)
        # 从本地文件系统中加载当前job对应的模型，此时需要判断收集到的模型数量是否达到目标要求
        # 若在一定时间内当前聚合的模型数量仍然未达到目标要求则先暂停当前job

        # 当收集到的模型达到目标要求时，加载模型

        # 使用聚合算法对当前收集到的模型进行聚合

        # 存储聚合后的模型，并将聚合后的模型发送给其他节点
        pass

    def status(self):
        pass

    def stop(self):
        pass

    def is_available(self):
        pass

    def is_running(self):
        pass

    def is_finished(self):
        pass

    def aggregate(self):
        pass

    def is_models_avaliable(self, target_num):
        """
        统计指定文件夹中模型文件的数量
        Parameters
        ----------
        target_num: 目标的模型数量

        Returns 是否收集到指定数量的模型
        -------

        """
        # 获取当前的训练轮次
        job_id = self.job.job_id
        cur_round = self.job.round
        path_util = JobPath(job_id)
        # 全局模型的输出路径
        global_model_path = path_util.global_params_dir(cur_round)
        # 客户端模型的获取路径
        client_model_paths = self.get_client_model_paths(job_id, cur_round)
        avaliable_client_model_paths = []
        avaliable_client_num = 0
        for client_model_path in client_model_paths:
            if os.path.exists(client_model_path):
                avaliable_client_model_paths.append(client_model_path)
                avaliable_client_num += 1
        if avaliable_client_num >= target_num:
            return avaliable_client_model_paths
        else:
            return None



    def get_client_model_paths(self, job_id, cur_round) -> List[str]:
        """
        获取客户端的模型存储路径
        Returns
        -------

        """
        path_util = JobPath(job_id)
        client_model_paths = []
        client_infos = get_client_by_job_id(job_id)
        for client_info in client_infos:
            client_model_paths.append(path_util.client_params_dir(cur_round, client_info.address) + f"/{job_id}.pth")
        return client_model_paths

class JobTrainScheduler(JobScheduler):

    def __init__(self, *, node: GflNode, job: Job):
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

    def is_available(self):
        pass

    def is_running(self):
        pass

    def is_finished(self):
        pass

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
