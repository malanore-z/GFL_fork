import gfl_test

from gfl.core.manager import JobManager, DatasetManager
from gfl.core.manager.generator import DatasetGenerator, JobGenerator
from gfl.core.strategy import *

import gfl_test.model as fl_model
import gfl_test.dataset as fl_dataset


def generate_dataset():
    generator = DatasetGenerator(fl_dataset)
    generator.metadata.content = "mnist dataset"
    generator.dataset_config.with_dataset(fl_dataset.mnist_dataset)
    generator.dataset_config.with_val_rate(0.2)
    dataset = generator.generate()
    DatasetManager.submit_dataset(dataset)
    print(dataset.dataset_id)


def generate_job():
    generator = JobGenerator(fl_model)
    generator.metadata.content = "mnist CNN"
    generator.job_config.with_trainer(TrainerStrategy.SUPERVISED)
    generator.job_config.with_aggregator(AggregatorStrategy.FED_AVG)
    generator.train_config.with_model(fl_model.model)
    generator.train_config.with_optimizer(fl_model.MnistOptimizer, lr=0.2)
    generator.train_config.with_loss(fl_model.CrossEntropyLoss)
    generator.aggregate_config.with_round(3)
    job = generator.generate()
    JobManager.submit_job(job)
    print(job.job_id)


if __name__ == "__main__":
    generate_dataset()
    generate_job()
