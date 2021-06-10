import os

import gfl.core.lfs as lfs
from gfl.core.manager.manager import Manager
from gfl.core.manager.sql_execute import *
from gfl.net import NetBroadcast


class JobManager(Manager):
    def __init__(self):
        pass

    @classmethod
    def submit_job(cls, job):
        # 1、节点提交job，将job信息记录到数据库
        # 2、并将这个job广播出去
        # server直接调用submit_job方法可以提交任务并广播任务。
        lfs.save_job(job)
        job_file = lfs.load_job_zip(job.job_id)
        NetBroadcast.broadcast_job(job.job_id, job_file)

    @classmethod
    def save_job(cls, job):
        lfs.save_job(job)

    @classmethod
    def unfinished_jobs(cls):
        lfs_jobs = lfs.load_all_job()
        jobs = []
        for job in lfs_jobs:
            status = get_kv(job.job_id, "status")
            if status != "finish":
                jobs.append(job)
        return jobs

    @classmethod
    def init_job_sqlite(cls, job_id):
        create_tables(job_id)
