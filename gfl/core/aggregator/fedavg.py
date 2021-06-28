import random

import torch
from torch.utils.data import DataLoader

from gfl.conf.node import GflNode
from gfl.core.aggregator.aggregator import Aggregator
from gfl.core.data import Job
from gfl.net.standlone import *
from gfl.core.lfs.path import JobPath


class FedAvgAggregator(Aggregator):
    def __init__(self, job: Job, server: GflNode = GflNode.default_node):
        super(FedAvgAggregator, self).__init__(job, server)

    def aggregate(self):
        n_total_samples = sum([report["n_samples"] for report in self.reports.values()])
        for idx, client in enumerate(self.selected_clients):
            model = NetReceive.receive(client, self.job_id, self.step, self.job_id)
            weight = self.reports[client]["n_samples"] / n_total_samples
            for key in model.keys():
                model[key] *= weight
            if idx == 0:
                averaged_model = model
            else:
                for key in model.keys():
                    averaged_model[key] += model[key]
        self.global_model_weights = averaged_model

    def choose_clients(self):
        assert self.clients_per_round <= len(self.available_clients)
        self.selected_clients = random.sample(list(self.available_clients), self.clients_per_round)

    def evaluate(self):
        model = self.job.train_config.get_model()
        model.load_state_dict(self.global_model_weights)
        val_dataloader = DataLoader(self.dataset, batch_size=self.batch_size)
        size = len(self.dataset)
        test_loss, correct = 0, 0
        with torch.no_grad():
            for X, y in val_dataloader:
                pred = model(X)
                test_loss += self.loss(pred, y).item()
                correct += (pred.argmax(1) == y).type(torch.float).sum().item()
        test_loss /= size
        correct /= size
        print(f"loss: {test_loss}  acc: {correct} ")
        return test_loss, correct

    def aggregate_evaluate(self):
        n_total_samples = sum([report["n_samples"] for report in self.reports.values()])
        for idx, client in enumerate(self.selected_clients):
            weight = self.reports[client]["n_samples"] / n_total_samples
            weighted_val_losses = [report["n_samples"] * report["val_loss"] for report in self.reports.values()]
            weighted_accuracy = [report["n_samples"] * report["val_acc"] for report in self.reports.values()]

    def check_should_stop(self):
        """
        判断是否需要停止训练
        Returns
        -------

        """
        if self.step >= self.target_round:
            self.should_stop = True