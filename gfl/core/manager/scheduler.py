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

    def __init__(self, *, node: GflNode, job, target_num):
        super(JobAggregateScheduler, self).__init__(node=node, job=job)
        self.clients = set()
        self.target_num = target_num
        self.client_model_params = {}
        self.__status = JobStatus.RESOURCE_NOT_ALREADY
        self.__target_round = self.job.aggregate_config.get_round()
        self.update_clients()
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
        print("开始聚合，轮次：" + str(self.job.cur_round))
        self.aggregate()
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
        # 获取模型前先更新客户端
        self.update_clients()
        job_id, cur_round = self.job.job_id, self.job.cur_round
        for client_addr in self.clients:
            if client_addr not in self.client_model_params:
                client_model_params = StandaloneReceive.receive_partial_params(client_addr, job_id, cur_round)
                if client_model_params is not None:
                    self.client_model_params[client_addr] = client_model_params
        if len(self.client_model_params) >= self.target_num:
            self.__status = JobStatus.RESOURCE_ALREADY
            return True
        else:
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

    def aggregate(self):
        print("聚合方开始模型聚合")
        job_id = self.job.job_id
        step = self.job.cur_round
        # 调用aggregator进行模型的聚合
        self.job.job_config.aggregator.is_instance = True
        aggregator_clazz = self.job.job_config.get_aggregator()
        aggregator = aggregator_clazz(job=self.job, step=step)
        # aggregator._post_aggregate() 需要将训练好的模型进行保存
        global_model_params = aggregator.aggregate(self.client_model_params)
        StandaloneBroadcast.broadcast_global_params(job_id, step, global_model_params)
        self.client_model_params = {}
        self.__status = JobStatus.EPOCH_FINISHED

    def update_clients(self):
        """
        获取并且更新当前节点的client的地址
        Returns
        -------

        """
        client = StandaloneReceive.receive_cmd_register(self.job.job_id)
        while client is not None:
            self.clients.add(client['address'])
            client = StandaloneReceive.receive_cmd_register(self.job.job_id)

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
            self.__model_params_path = StandaloneReceive.receive_global_params(job_id=self.job.job_id,
                                                                               cur_round=self.job.cur_round)

        if self.__model_params_path is None:
            return False
        else:
            # resources_already:1
            self.__status = JobStatus.RESOURCE_ALREADY
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
