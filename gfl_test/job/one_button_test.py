import gfl_test

import os
from pathlib import PurePath

from gfl.conf import GflPath
from gfl.core.config import *
from gfl.core.manager import DatasetManager, JobManager
from gfl.core.strategy import LRSchedulerStrategy
from gfl.core.trainer import SupervisedTrainer

import gfl_test.dataset as gfl_dataset
import gfl_test.model as gfl_model


def generate_dataset():
    dataset_config = DatasetConfig().with_dataset("mnist_dataset").with_val_rate(0.3)
    return DatasetManager.generate_dataset(gfl_dataset, dataset_config)


def generate_job():
    train_config = TrainConfig(epoch=2, batch_size=32)\
            .with_model(gfl_model.Net)\
            .with_loss(gfl_model.CrossEntropyLoss)\
            .with_optimizer(gfl_model.MnistOptimizer, lr=0.01)\
            .with_lr_scheduler(LRSchedulerStrategy.ReduceLROnPlateau, mode="max", factor=0.5, patience=5)
    aggregate_config = AggregateConfig()
    job_config = JobConfig(round=3)
    job = JobManager.generate_job(gfl_model, job_config, train_config, aggregate_config)
    return job.job_id


def prepare(job_id, dataset_id):
    JobManager.submit_job(job_id)
    JobManager.fetch_job(job_id, dataset_id)


def train(job_id):
    job = JobManager.load_client_job(job_id)
    trainer = SupervisedTrainer(job)
    trainer.train()


if __name__ == "__main__":
    dataset_id = generate_dataset()
    job_id = generate_job()
    prepare(job_id, dataset_id)

    work_dir = PurePath(GflPath.work_dir, job_id).as_posix()
    print("Console output is redirected to:")
    console_out_path = PurePath(work_dir, "console_out").as_posix()
    console_out_path = os.path.abspath(console_out_path)
    console_out_path = PurePath(console_out_path).as_posix()
    print(console_out_path)

    train(job_id)

    print("-*-*-*-*-*-*-*-")
    print("Train finished.")
    print("-*-*-*-*-*-*-*-")

    print("You can find train result under the folder:")
    abs_work_dir = os.path.abspath(work_dir)
    abs_work_dir = PurePath(abs_work_dir).as_posix()
    print(abs_work_dir)
