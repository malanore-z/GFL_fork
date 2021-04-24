import torch

from gfl.conf.node import GflNode
from gfl.core.aggregator.aggregator import Aggregator
from gfl.core.data import Job
from gfl.core.lfs.path import JobPath


class FedAvgAggregator(Aggregator):

    def __init__(self, job: Job, step: int, server: GflNode = GflNode.default_node):
        super(FedAvgAggregator, self).__init__(job, step, server)
        self.global_param = None

    def _aggregate(self, client_model_params):
        n_models = len(client_model_params)
        averaged_param = client_model_params[0]
        weight = 1 / n_models
        for key in averaged_param.keys():
            for idx, client_model_param in enumerate(client_model_params):
                if idx == 0:
                    averaged_param[key] *= weight
                if idx != 0:
                    averaged_param[key] += (client_model_param[key] * weight)
        self.global_model_param = averaged_param

    def _post_aggregate(self):
        # 完成指定聚合之后保存当前模型
        # 在 standalone 模式下，将聚合后的模型保存到指定位置
        global_model_path = JobPath(self.job_id).global_params_dir(self.job.cur_round+1)
        # 将聚合后的模型参数保存在指定路径上
        torch.save(self.global_model_param, global_model_path)
        # 判断此时模型是否已经训练完成
