

import gfl.core.lfs as lfs
from gfl.conf import GflNode
from gfl.core.config import *
from gfl.core.data import Job, JobMetadata
from gfl.core.manager.manager import Manager
from gfl.net import *


class JobManager(Manager):

    @classmethod
    def generate_job(cls, module,
                     metadata: JobMetadata = JobMetadata(),
                     job_config: JobConfig = JobConfig(),
                     train_config: TrainConfig = TrainConfig(),
                     aggregate_config: AggregateConfig = AggregateConfig()) -> Job:
        """

        :param module:
        :param job_config:
        :param train_config:
        :param aggregate_config:
        :return:
        """
        job_id = cls.generate_job_id()
        if job_config.owner is None:
            job_config.owner = GflNode.address
        job = Job(job_id=job_id,
                  metadata=metadata,
                  job_config=job_config,
                  train_config=train_config,
                  aggregate_config=aggregate_config)
        lfs.save_job(job, module)
        return job

    @classmethod
    def submit_job(cls, job_id):
        job = lfs.load_job(job_id)
        NetBroadcast.broadcast_job(job_id, job) # TODO: cast job to zip
