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

    def __init__(self, *, node: GflNode, job, target_num):
        super(JobAggregateScheduler, self).__init__(node=node, job=job)
        self.client_model_paths = []
        self.target_num = target_num
        self.avaliable_models = set()
        self.client_model_params = []
        self.__status = JobStatus.RESOURCE_NOT_ALREADY
        self.__target_round = self.job.aggregate_config.get_round()
        # 若当前的训练轮次为0，则需要聚合方生成一个初始的全局模型分发给各个训练方
        if self.job.cur_round == 0:
            self.init_global_model()

    def start(self):
        """
        启动一轮训练
        Returns
        -------

        """
        # 使用聚合算法对当前收集到的模型进行聚合
        self.job.cur_round += 1
        print("开始聚合，轮次："+str(self.job.cur_round))
        self.aggregate(list(self.avaliable_models))
        self.is_finished()

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
        job_id, cur_round = self.job.job_id, self.job.cur_round
        # 获取客户端模型的存储路径
        self.client_model_paths = self.get_client_model_paths(job_id, cur_round)
        # 获得客户端已经准备好的模型的存储路径，保存到 avaliable_models 中
        self.get_avaliable_models()
        # 达到阈值
        if len(self.client_model_paths) >= self.target_num:
            self.__status = JobStatus.RESOURCE_ALREADY
            return True
        else:
            # 若训练完成的客户端数量未达到阈值，则初始化以下参数，以便下次调用
            self.client_model_paths = []
            self.avaliable_models = set()
            self.client_model_params = []
            return False

    def init_global_model(self):
        job_id = self.job.job_id
        path_util = JobPath(self.job.job_id)
        global_model_path = path_util.global_params_dir(0)
        os.makedirs(global_model_path, exist_ok=True)
        global_model_path += f"/{job_id}.pth"
        torch.save(self.job.train_config.get_model().state_dict(), global_model_path)

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

    def aggregate(self, client_model_paths):
        """
        加载从client获得的模型参数，调用aggregator进行模型的聚合
        Parameters
        ----------
        client_model_paths: List[str]
            保存模型路径的List
        Returns
        -------

        """
        # 加载从client获得的模型参数
        for client_model_path in client_model_paths:
            try:
                client_model_param = torch.load(client_model_path)
                self.client_model_params.append(client_model_param)
            except:
                raise ValueError(f"模型 {client_model_path} 加载失败")
        # 调用aggregator进行模型的聚合
        self.job.job_config.aggregator.is_instance = True
        aggregator_clazz = self.job.job_config.get_aggregator()
        aggregator = aggregator_clazz(job=self.job, step=self.job.cur_round)
        # aggregator._post_aggregate() 需要将训练好的模型进行保存
        aggregator.aggregate(self.client_model_params)
        self.client_model_paths = []
        self.avaliable_models = set()
        self.client_model_params = []
        self.__status = JobStatus.EPOCH_FINISHED

    def get_avaliable_models(self):
        """
        获得从客户端已经接收到的模型
        Returns List[str]
            返回的是对包含对应模型文件路径的List
        -------

        """
        for client_model_path in self.client_model_paths:
            self.avaliable_models.add(client_model_path)

    @staticmethod
    def get_client_model_paths(job_id, cur_round) -> List[str]:
        """
        获取客户端的模型存储路径
        Returns
        -------

        """
        path_util = JobPath(job_id)
        client_model_paths = []
        client_infos = get_client_by_job_id(job_id)
        print(client_infos)
        for client_info in client_infos:
            client_model_path = path_util.client_params_dir(cur_round, client_info.address) + f"/{job_id}.pth"
            if os.path.exists(client_model_path):
                client_model_paths.append(client_model_path)
                print("聚合方获取训练方的模型：" + str(client_model_path))
        return client_model_paths


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
        trainer.model.load_state_dict(torch.load(model_params_path))
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
        model_params_path = PathUtils.join(global_params_dir, job_id + '.pth')
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
