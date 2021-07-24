__all__ = [
    "DatasetMetadata",
    "JobMetadata",
    "Dataset",
    "Job"
]

from gfl.core.config import DatasetConfig, TrainConfig, AggregateConfig, JobConfig
from gfl.utils.po_utils import PlainObject


class Metadata(PlainObject):

    id: str = None
    owner: str = None
    create_time: int
    content: str


class DatasetMetadata(Metadata):

    pass


class JobMetadata(Metadata):

    pass


class Dataset(object):

    def __init__(self, *,
                 dataset_id: str = None,
                 metadata: DatasetMetadata = None,
                 dataset_config: DatasetConfig = None):
        super(Dataset, self).__init__()
        self.module = None
        self.dataset_id = dataset_id
        self.metadata = metadata
        self.dataset_config = dataset_config


class Job(object):

    def __init__(self, *,
                 job_id: str = None,
                 metadata: JobMetadata = None,
                 job_config: JobConfig = None,
                 train_config: TrainConfig = None,
                 aggregate_config: AggregateConfig = None):
        super(Job, self).__init__()
        self.module = None
        self.job_id = job_id
        self.cur_round = 0
        self.metadata = metadata
        self.job_config = job_config
        self.train_config = train_config
        self.aggregate_config = aggregate_config
        self.dataset = None

    def mount_dataset(self, dataset: Dataset):
        self.dataset = dataset
