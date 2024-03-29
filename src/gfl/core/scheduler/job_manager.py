import gfl.core.lfs as lfs
from gfl.core.data import Job
from gfl.core.scheduler.manager import Manager
from gfl.core.scheduler.sql_execute import *
from gfl.net import NetBroadcast


class JobManager(Manager):

    @classmethod
    def submit_job(cls, job: Job):
        lfs.save_job(job)
        job_file = lfs.load_job_zip(job.job_id)
        NetBroadcast.broadcast_job(job.job_id, job_file)
        save_kv(job_id=job.job_id, kv=KVEntity("status", "waiting"))

    @classmethod
    def cancel_job(cls, job_id):
        update_kv(job_id=job_id, kv=KVEntity("status", "fail"))

    @classmethod
    def finish_job(cls, job_id):
        update_kv(job_id=job_id, kv=KVEntity("status", "finish"))

    @classmethod
    def start_job(cls, job_id):
        update_kv(job_id=job_id, kv=KVEntity("status", "running"))

    @classmethod
    def unfinished_jobs(cls):
        lfs_jobs = lfs.load_all_job()
        jobs = []
        for job in lfs_jobs:
            status = get_kv(job.job_id, "status")[0]
            if status.value == "waiting":
                jobs.append(job)
        return jobs

    @classmethod
    def init_job_sqlite(cls, job_id):
        create_tables(job_id)
