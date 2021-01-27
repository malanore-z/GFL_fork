from gfl.core.config import *


class Job(object):

    def __init__(self,
                 job_id: str,
                 job_config: JobConfig,
                 train_config: TrainConfig,
                 aggregate_config: AggregateConfig):
        super(Job, self).__init__()
        self.job_id = job_id
        self.job_config = job_config
        self.train_config = train_config
        self.aggregate_config = aggregate_config


class ServerJob(object):

    def __init__(self,
                 job_id: str,
                 job_config: JobConfig,
                 train_config: TrainConfig,
                 aggregate_config: AggregateConfig):
        super(ServerJob, self).__init__(job_id, job_config, train_config, aggregate_config)


class ClientJob(object):

    def __init__(self,
                 job_id: str,
                 job_config: JobConfig,
                 train_config: TrainConfig,
                 aggregate_config: AggregateConfig):
        super(ClientJob, self).__init__(job_id, job_config, train_config, aggregate_config)
        self.dataset_config = None

    def mount_dataset(self, dataset_config: DatasetConfig):
        self.dataset_config = dataset_config
