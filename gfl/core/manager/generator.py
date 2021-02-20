__all__ = [
    "DatasetGenerator",
    "JobGenerator"
]

import abc
import time
import uuid

from gfl.conf.node import GflNode
from gfl.core.data.config import *
from gfl.core.data.metadata import JobMetadata, DatasetMetadata
from gfl.core.data.dataset import Dataset
from gfl.core.data.job import Job
from gfl.utils import TimeUtils


class Generator(object):

    JOB_NAMESPACE = uuid.UUID(GflNode.address[:31] + '1')
    DATASET_NAMESPACE = uuid.UUID(GflNode.address[:31] + "2")

    def __init__(self, module):
        super(Generator, self).__init__()
        self.module = module

    @abc.abstractmethod
    def generate(self):
        pass

    @classmethod
    def __generate_uuid(cls, namespace):
        nano_time = int(int(1e9) * time.time())
        name = GflNode.address[31:] + str(nano_time / 100)
        return uuid.uuid3(namespace, name).hex.replace("-", "")

    @classmethod
    def _generate_job_id(cls):
        return cls.__generate_uuid(cls.JOB_NAMESPACE)

    @classmethod
    def _generate_dataset_id(cls):
        return cls.__generate_uuid(cls.DATASET_NAMESPACE)


class DatasetGenerator(Generator):

    def __init__(self, module):
        super(DatasetGenerator, self).__init__(module)
        self.dataset_id = self._generate_dataset_id()
        self.metadata = DatasetMetadata(id=self.dataset_id,
                                        owner=GflNode.address,
                                        create_time=TimeUtils.millis_time())
        self.dataset_config = DatasetConfig(module=module)

    def generate(self):
        dataset = Dataset(dataset_id=self.dataset_id,
                          metadata=self.metadata,
                          dataset_config=self.dataset_config)
        dataset.module = self.module
        return dataset


class JobGenerator(Generator):

    def __init__(self, module):
        super(JobGenerator, self).__init__(module)
        self.job_id = self._generate_job_id()
        self.metadata = JobMetadata(id=self.job_id,
                                    owner=GflNode.address,
                                    create_time=TimeUtils.millis_time())
        self.job_config = JobConfig(module=module)
        self.train_config = TrainConfig(module=module)
        self.aggregate_config = AggregateConfig(module=module)

    def generate(self):
        job = Job(job_id=self.job_id,
                  metadata=self.metadata,
                  job_config=self.job_config,
                  train_config=self.train_config,
                  aggregate_config=self.aggregate_config)
        job.module = self.module
        return job
