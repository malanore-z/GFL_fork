import abc
import os

import torch

from gfl.conf.node import GflNode
from gfl.core.context import WorkDirContext
from gfl.core.data import Job
from gfl.core.data.config import AggregateConfig
from gfl.core.lfs.path import JobPath
from gfl.utils import TimeUtils, PathUtils


class Aggregator(object):

    def __init__(self, job: Job, step: int, server: GflNode = GflNode.default_node):
        super(Aggregator, self).__init__()
        self.global_model_param = None
        self.start_time = TimeUtils.millis_time()
        self.job = job
        self.step = step
        self.server = server
        self.job_id = job.job_id
        self._parse_aggregate_config(job.aggregate_config)

    def aggregate(self, client_model_params):
        job_path = JobPath(self.job_id)
        work_dir = job_path.server_work_dir(self.step)
        os.makedirs(work_dir, exist_ok=True)
        with WorkDirContext(work_dir):
            self._pre_aggregate()
            self._aggregate(client_model_params)
            self._post_aggregate()
        # 完成指定聚合之后保存当前模型
        # 在 standalone 模式下，将聚合后的模型保存到指定位置
        global_params_path = JobPath(self.job_id).global_params_dir(self.job.cur_round)
        os.makedirs(global_params_path, exist_ok=True)
        path = PathUtils.join(global_params_path, self.job_id + '.pth')
        # 将聚合后的模型参数保存在指定路径上
        print("聚合完成，已经模型保存至：" + str(global_params_path))
        torch.save(self.global_model_param, path)
        # 判断此时模型是否已经训练完成

    def _pre_aggregate(self):
        pass

    @abc.abstractmethod
    def _aggregate(self, client_model_params):
        raise NotImplementedError("")

    def _post_aggregate(self):
        pass

    def _parse_aggregate_config(self, aggregate_config: AggregateConfig):
        pass
