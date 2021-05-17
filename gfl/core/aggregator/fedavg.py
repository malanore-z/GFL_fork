import random

import torch

from gfl.conf.node import GflNode
from gfl.core.aggregator.aggregator import Aggregator
from gfl.core.data import Job
from gfl.net.standlone import *
from gfl.core.lfs.path import JobPath


class FedAvgAggregator(Aggregator):
    def __init__(self, job: Job, server: GflNode = GflNode.default_node):
        super(FedAvgAggregator, self).__init__(job, server)

    def aggregate(self):
        n_clients = len(self.selected_clients)
        for idx, client in enumerate(self.selected_clients):
            model = NetReceive.receive(client, self.job_id, self.step, self.job_id)
            weight = 1 / n_clients
            for key in model.keys():
                model[key] *= weight
            if idx == 0:
                averaged_model = model
            else:
                for key in model.keys():
                    averaged_model[key] += model[key]
        self.global_model = averaged_model

    def choose_clients(self):
        assert self.clients_per_round <= len(self.available_clients)
        self.selected_clients = random.sample(list(self.available_clients), self.clients_per_round)