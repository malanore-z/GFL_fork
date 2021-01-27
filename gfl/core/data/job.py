
from gfl.core.config import TrainConfig, AggregateConfig, JobConfig
from gfl.core.data.metadata import JobMetadata


class Job(object):

    def __init__(self,
                 job_id: str,
                 metadata: JobMetadata = None,
                 job_config: JobConfig = None,
                 train_config: TrainConfig = None,
                 aggregate_config: AggregateConfig = None):
        super(Job, self).__init__()
        self.job_id = job_id
        self.metadata = metadata
        self.job_config = job_config
        self.train_config = train_config
        self.aggregate_config = aggregate_config
        self.dataset_config = None

    def mount_dataset(self, dataset_id: str):
        pass
