import gfl_test

from gfl.conf import GflPath
from gfl.core.config import TrainConfig, JobConfig, AggregateConfig
from gfl.core.strategy import LRSchedulerStrategy
from gfl.core.manager import JobManager

import gfl_test.model as gfl_model


if __name__ == "__main__":
    train_config = TrainConfig(epoch=10, batch_size=32)\
            .with_model(gfl_model.Net)\
            .with_loss(gfl_model.CrossEntropyLoss)\
            .with_optimizer(gfl_model.MnistOptimizer, lr=0.01)\
            .with_lr_scheduler(LRSchedulerStrategy.ReduceLROnPlateau, mode="max", factor=0.5, patience=5)
    aggregate_config = AggregateConfig()
    job_config = JobConfig(round=3)
    job = JobManager.generate_job(gfl_model, job_config, train_config, aggregate_config)
    print(job.job_id)

    JobManager.submit_job(job.job_id)
