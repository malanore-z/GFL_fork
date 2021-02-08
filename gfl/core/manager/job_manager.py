

import gfl.core.lfs as lfs
from gfl.core.data import Job
from gfl.core.manager.manager import Manager
from gfl.net import NetBroadcast


class JobManager(Manager):

    @classmethod
    def submit_job(cls, job: Job):
        lfs.save_job(job)
        job_file = lfs.load_job_zip(job.job_id)
        NetBroadcast.broadcast_job(job.job_id, job_file)
