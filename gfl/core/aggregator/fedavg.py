import torch

from gfl.conf.node import GflNode
from gfl.core.aggregator.aggregator import Aggregator
from gfl.core.data import Job
from gfl.core.lfs.path import JobPath


class FedAvgAggregator(Aggregator):

    def __init__(self, job: Job, step: int, server: GflNode = GflNode.default_node):
        super(FedAvgAggregator, self).__init__(job, step, server)

    def _aggregate(self, client_model_params):
        """
        聚合模型
        Parameters
        ----------
        client_model_params: dict, {address: model}
            保存每个客户端对应的模型
        Returns
        -------

        """
        n_models = len(client_model_params)
        client_model_params_list = list(client_model_params.values())
        averaged_param = client_model_params_list[0]
        weight = 1 / n_models
        for key in averaged_param.keys():
            for idx, client_model_param in enumerate(client_model_params_list):
                if idx == 0:
                    averaged_param[key] *= weight
                if idx != 0:
                    averaged_param[key] += (client_model_param[key] * weight)
        self.global_model_param = averaged_param
