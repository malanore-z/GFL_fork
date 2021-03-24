import abc
import os
from typing import List

from gfl.conf import GflConf
from gfl.conf.node import GflNode
from gfl.core.trainer import SupervisedTrainer
from gfl.core.lfs.path import JobPath
from gfl.core.manager.sql_execute import *


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

    def __init__(self, node, job):
        super(JobTrainScheduler, self).__init__(node=node, job=job)
        self.trainer = None
        self.status = None

    def start(self):
        # 解析Job中的模型参数与数据参数

        # 判断模型与数据是否可用/存在，不满足则waiting，实例化模型与数据

        # 调用trainer对模型进行训练

        # 完成指定轮次的训练之后保存当前模型的训练状态

        # 将经过训练的模型发送给聚合方进行聚合，等待聚合后的模型
        pass

    def status(self):
        # resources_not_already: 0
        # resources_already: 1
        # training: 2
        # epoch_finished: 3
        # all_finished: 4
        # 直接返回任务的状态：self.status
        # 在其他涉及状态相关的函数调用时更新self.status
        pass

    def stop(self):
        pass

    def register(self):
        pass

    def train(self, step):
        """
        训练指定的epoch后再返回模型，用于聚合
        Parameters
        ----------
        step: 训练的步长

        Returns trainer
        -------

        """
        trainer_clazz = self.job.job_config.get_trainer()
        trainer = trainer_clazz(job=self.job, step=0, client=self.node)
        trainer.train()

    def load_data(self):
        """
        加载训练数据，返回对应的数据集，若无数据集，则返回None
        Returns
        -------

        """
        pass

    def load_model(self):
        """
        加载训练模型，返回对应的模型，若无模型，则返回None
        Returns
        -------

        """
        pass