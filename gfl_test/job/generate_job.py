import gfl_test

import time


from gfl.core.manager import JobManager, DatasetManager
from gfl.core.data import *
from gfl.core.data.config import *
from gfl.core.strategy import *

import gfl_test.model as fl_model
import gfl_test.dataset as fl_dataset


def generate_dataset():
    metadata = DatasetMetadata(create_time=int(1000 * time.time()), content="mnist dataset")
    dataset_config = DatasetConfig(module=fl_dataset, )
    dataset_config.with_dataset(fl_dataset.mnist_dataset)
    dataset_config.with_val_rate(0.2)
    dataset = DatasetManager.generate_dataset(fl_dataset, metadata, dataset_config)
    print(dataset.dataset_id)


def generate_job():
    metadata = JobMetadata(create_time=int(1000 * time.time()), content="mnist CNN")
    job_config = JobConfig(module=fl_model)
    job_config.with_trainer(TrainerStrategy.SUPERVISED)
    job_config.with_aggregator(AggregatorStrategy.FED_AVG)
    train_config = TrainConfig(module=fl_model)
    train_config.with_model(fl_model.Net)
    train_config.with_optimizer(fl_model.MnistOptimizer, lr=0.1)
    train_config.with_loss(fl_model.CrossEntropyLoss)
    aggregate_config = AggregateConfig(module=fl_model)
    aggregate_config.round = 3
    job = JobManager.generate_job(module=fl_model,
                                  metadata=metadata,
                                  job_config=job_config,
                                  train_config=train_config,
                                  aggregate_config=aggregate_config)
    print(job.job_id)


if __name__ == "__main__":
    generate_job()
