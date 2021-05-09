import json

import torch
from torch.utils.data import random_split, DataLoader

import gfl.gfl as gfl
from gfl.conf.node import GflNode
from gfl.core.data import Job
from gfl.core.trainer.trainer import Trainer
from gfl.core.lfs.path import *


class SupervisedTrainer(Trainer):

    def __init__(self, job: Job, step: int, client: GflNode = GflNode.default_node):
        super(SupervisedTrainer, self).__init__(job, step, client)

    def _pre_train(self):
        super(SupervisedTrainer, self)._pre_train()
        self.train_dataloader = DataLoader(self.dataset, batch_size=self.batch_size)
        self.val_dataloader = DataLoader(self.val_dataset, batch_size=self.batch_size)
        self.model = self.model.to(gfl.device)

    def _train(self):
        self.history = {
            "train_loss": [],
            "train_acc": [],
            "val_loss": [],
            "val_acc": []
        }
        for e in range(self.epoch):
            t_loss, t_correct, t_total = self.__epoch_train(self.train_dataloader)
            with torch.no_grad():
                v_loss, v_correct, v_total = self.__epoch_train(self.val_dataloader)
            print("EPOCH %d OF %d" % (e, self.epoch))
            print("\tTrain Loss: %s, Acc: %s" % (t_loss, t_correct / t_total))
            print("\tVal   Loss: %s, Acc: %s" % (v_loss, v_correct / v_total), flush=True)

            self.history["train_loss"].append(t_loss)
            self.history["train_acc"].append(t_correct / t_total)
            self.history["val_loss"].append(v_loss)
            self.history["val_acc"].append(v_correct / v_total)

    def _post_train(self):
        super(SupervisedTrainer, self)._post_train()
        with open("history.json", "w") as f:
            f.write(json.dumps(self.history, indent=4))

    def _validate(self):
        pass

    def _split_dataset(self, dataset, rate):
        dataset_len = len(dataset)
        val_len = int(rate * dataset_len)
        train_len = dataset_len - val_len
        return random_split(dataset, (train_len, val_len))

    def __epoch_train(self, dataloader: DataLoader):
        correct = 0
        total = 0
        loss_v = 0
        iter_num = 0

        for i, data in enumerate(dataloader):
            inputs, labels = data
            inputs = inputs.to(gfl.device)
            labels = labels.to(gfl.device)

            if torch.is_grad_enabled():
                self.optimizer.zero_grad()

            outputs = self.model(inputs)
            loss = self.loss(outputs, labels)

            if torch.is_grad_enabled():
                loss.backward()
                self.optimizer.step()

            loss_v += loss.item()
            iter_num += 1

            _, pred = torch.max(outputs, 1)
            c = (pred == labels).squeeze()
            for i, lb in enumerate(labels):
                correct += c[i].item()
                total += 1

        return loss_v / iter_num, correct, total
