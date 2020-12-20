import sqlite3

from gfl.core.config import TrainConfig, AggregateConfig, JobConfig, DatasetConfig


class Job(object):

    def __init__(self, job_id: str,
                 job_config: JobConfig = None,
                 train_config: TrainConfig = None,
                 aggregate_config: AggregateConfig = None,
                 dataset_config: DatasetConfig = None):
        super(Job, self).__init__()
        self.job_id: str = job_id
        self.job_config = job_config
        self.train_config = train_config
        self.aggregate_config = aggregate_config
        self.dataset_config = dataset_config


class ServerJob(Job):

    pass


class ClientJob(Job):

    pass