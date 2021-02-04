import os

from gfl.conf.node import GflNode
from gfl.core.context import WorkDirContext
from gfl.core.data import Job
from gfl.core.data.config import TrainConfig, DatasetConfig
from gfl.core.lfs.path import JobPath
from gfl.utils import TimeUtils


class Trainer(object):

    """
        epoch: int = 10
    batch_size: int = 32
    model: ConfigObject
    optimizer: ConfigObject
    lr_scheduler: ConfigObject
    loss: ConfigObject
    """
    def __init__(self, job: Job, step: int, client: GflNode = GflNode.default_node):
        super(Trainer, self).__init__()
        self.job_start_time = TimeUtils.millis_time()
        self.step = step
        self.client = client
        self.job_id = job.job_id
        self.model = None
        self.optimizer = None
        self.lr_scheduler = None
        self.loss = None
        self.epoch = None
        self.batch_size = None
        self.dataset = None
        self.val_dataset = None
        self._parse_train_config(job.train_config)
        self._parse_dataset_config(job.dataset.dataset_config)

    def train(self):
        job_path = JobPath(self.job_id)
        work_dir = job_path.client_work_dir(self.step, self.client.address)
        os.makedirs(work_dir, exist_ok=True)
        with WorkDirContext(work_dir):
            self._pre_train()
            self._train()
            self._post_train()

    def validate(self):
        pass

    def _parse_train_config(self, train_config: TrainConfig):
        pass

    def _parse_dataset_config(self, dataset_config: DatasetConfig):
        pass

    def _pre_train(self):
        pass

    def _train(self):
        raise NotImplementedError("")

    def _post_train(self):
        pass

    def _validate(self):
        raise NotImplementedError("")