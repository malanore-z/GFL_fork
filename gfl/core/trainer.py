import json
import os
import time
from pathlib import PurePath

import matplotlib.pyplot as plt
import torch
from torch.utils.data import DataLoader, random_split

import gfl
from gfl.conf import GflPath
from gfl.core.job import ClientJob
from gfl.core.config import *
from gfl.core.context import WorkDirContext
from gfl.utils import ModuleUtils


class Trainer(object):
    """
    This class is the base class to define a training mode of a model.
    A variety of distributed model training modes can be realized by inheriting this class.
    """

    def __init__(self, job: ClientJob):
        super(Trainer, self).__init__()
        self.start_time = int(time.time())
        self.job = job
        self._parse_job_config(job.job_config)
        self._parse_train_config(job.train_config)
        self._parse_aggregate_config(job.aggregate_config)
        self._parse_dataset_config(job.dataset_config)

    def train(self):
        """
        Start training model: set context environment, modify working directory, redirect stdout and stderr and start
        training.
        """
        work_dir = os.path.join(GflPath.work_dir, self.job.job_id)
        os.makedirs(work_dir, exist_ok=True)
        with WorkDirContext(work_dir):
            self._pre_train()
            self._train()
            self._post_train()

    def _parse_job_config(self, job_config: JobConfig):
        """
        Parse job configuration: generate configuration parser to parse job configuration from serialized
        parameters. You can override this method in subclass to parse customization parameters.

        parameters:
            job_config: job configuration parameters which are serialized

        return:
            None
        """
        pass

    def _parse_train_config(self, train_config: TrainConfig):
        """
        Parse training configuration: generate configuration parser to parse model, loss, optimizer,
        etc. from serialized parameters. You can override this method in subclass to parse customization parameters.

        parameters:
            train_config: training configuration parameters which are serialized

        return:
            None
        """
        module_path = PurePath(GflPath.client_dir, self.job.job_id).as_posix()
        model_module = ModuleUtils.import_module(module_path, GflPath.model_module_name)
        config_parser = ConfigParser(model_module)
        self.model = config_parser.parse(train_config.model)
        self.loss = config_parser.parse(train_config.loss)
        self.optimizer = config_parser.parse(train_config.optimizer, self.model.parameters())
        self.lr_scheduler = config_parser.parse(train_config.lr_scheduler, self.optimizer)
        self.epoch = train_config.epoch
        self.batch_size = train_config.batch_size
        self.train_args = train_config.args

    def _parse_aggregate_config(self, aggregate_config: AggregateConfig):
        """
        Parse aggregating configuration: generate configuration parser to parse aggregating configuration from
        serialized parameters. You can override this method in subclass to parse customization parameters.

        parameters:
            aggregate_config: aggregating configuration parameters which are serialized

        return:
            None
        """
        pass

    def _parse_dataset_config(self, dataset_config: DatasetConfig):
        """
        Parse dataset configuration: generate configuration parser to parse dataset objects from serialized
        parameters. You can override this method in subclass to parse customization parameters.

        parameters:
            dataset_config: dataset configuration parameters which are serialized

        return:
            None
        """
        module_path = PurePath(GflPath.dataset_dir, dataset_config.id).as_posix()
        dataset_module = ModuleUtils.import_module(module_path, GflPath.dataset_module_name)
        config_parser = ConfigParser(dataset_module)
        self.dataset = config_parser.parse(dataset_config.dataset)
        self.val_dataset = config_parser.parse(dataset_config.val_dataset)
        if self.val_dataset is None:
            val_rate = dataset_config.val_rate
            dataset_len = len(self.dataset)
            val_dataset_len = int(val_rate * dataset_len)
            self.dataset, self.val_dataset = random_split(self.dataset,
                                                          [dataset_len - val_dataset_len, val_dataset_len])

    def _pre_train(self):
        """
        The preparation for model training. You can override this method in subclass.
        """
        self.model = self.model.to(gfl.device())

    def _train(self):
        """
        The model training method. You must override this method in subclass.
        """
        raise NotImplementedError("The sub class of Trainer must implement _train method.")

    def _post_train(self):
        """
        The environment cleaning and parameters saving after model training. You can override this method in subclass.
        """
        final_params_path = "params-%d" % self.start_time
        torch.save(self.model.state_dict(), final_params_path)


class SupervisedTrainer(Trainer):
    """
    This class inherits the Trainer and realized distributed supervised training mode.
    """

    def __init__(self, job: ClientJob):
        super(SupervisedTrainer, self).__init__(job)

    def _pre_train(self):
        """
        This method makes the preparation of model training, and generates dataloader and val_dataloader.
        """
        super(SupervisedTrainer, self)._pre_train()
        self.dataloader = DataLoader(self.dataset, batch_size=self.batch_size, shuffle=True)
        self.val_dataloader = DataLoader(self.val_dataset, batch_size=self.batch_size, shuffle=True)

    def _train(self):
        """
        This method makes the model training of the specified epochs.
        """
        self.history = {
            "train_loss": [],
            "train_acc": [],
            "valid_loss": [],
            "valid_acc": []
        }
        for i in range(self.epoch):
            t_l, t_a = self._epoch_train()
            self.history["train_loss"].append(t_l)
            self.history["train_acc"].append(t_a)
            v_l, v_a = self._epoch_valid()
            self.history["valid_loss"].append(v_l)
            self.history["valid_acc"].append(v_a)
            print("EPOCH %d of %d" % (i + 1, self.epoch), flush=True)
            print("      train_loss=%.4f, train_acc=%.2f" % (t_l, t_a), flush=True)
            print("      valid_loss=%.4f, valid_acc=%.2f" % (v_l, v_a), flush=True)

    def _post_train(self):
        """
        This method shows the loss and accuracy of model training in the train dataset and valid dataset,
        and makes the environment cleaning and parameters saving after model training.
        """
        super(SupervisedTrainer, self)._post_train()
        with open("history-%d.json" % self.start_time, "w") as f:
            f.write(json.dumps(self.history))
        plt.figure(figsize=(15, 5))

        plt.subplot(1, 2, 1)
        plt.plot(range(self.epoch), self.history["train_loss"], label="train")
        plt.plot(range(self.epoch), self.history["valid_loss"], label="valid")
        plt.title("Loss", size=15)
        plt.legend()
        plt.grid(True)

        plt.subplot(1, 2, 2)
        plt.plot(range(self.epoch), self.history["train_acc"], label="train")
        plt.plot(range(self.epoch), self.history["valid_acc"], label="valid")
        plt.title("Accuracy", size=15)
        plt.legend()
        plt.grid(True)

        plt.savefig("result-%d.png" % self.start_time)

    def _epoch_train(self):
        """
        This method makes a epoch of model training on the train dataset.

        """

        return self.__epoch_train(self.dataloader)

    def _epoch_valid(self):
        """
        This method gets the loss and accuracy of the current model on the valid dataset.

        """
        with torch.no_grad():
            return self.__epoch_train(self.val_dataloader)

    def __epoch_train(self, dataloader: DataLoader):
        """
        This method makes a epoch of model training.

        parameters:
            dataloader : DataLoader

        return:
            epoch_loss / iter_num: the loss of this epoch of training
            correct / total: the accuracy of this epoch of training
        """
        epoch_loss = 0.0
        iter_num = 0

        correct = 0
        total = 0

        for i, data in enumerate(dataloader, 0):
            inputs, labels = data
            inputs = inputs.to(gfl.device())
            labels = labels.to(gfl.device())

            if torch.is_grad_enabled():
                self.optimizer.zero_grad()

            outputs = self.model(inputs)

            loss = self.loss(outputs, labels)

            if torch.is_grad_enabled():
                loss.backward()
                self.optimizer.step()

            epoch_loss += loss.item()
            iter_num += 1

            _, predicted = torch.max(outputs, 1)
            c = (predicted == labels).squeeze()
            for i, lb in enumerate(labels):
                correct += c[i].item()
                total += 1

        return epoch_loss / iter_num, correct / total
