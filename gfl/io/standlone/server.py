import os
import time
from pathlib import PurePath

import gfl.io.aspect as aspect
from gfl.conf import GflPath
from gfl.core.manager import JobManager
from gfl.utils import ZipUtils


@aspect.Aspect(aspect.store_server_job, position="after")
def receive_published_job(job_id, job_ipfs, job):
    return job_id, job_ipfs, job


@aspect.Aspect(aspect.register_client)
def register_client(job_id, client):
    return job_id, client


@aspect.Aspect(aspect.load_server_job, position="before")
def broadcast_server_job(job_id, job_ipfs, job):
    return job_id, job_ipfs, job


def server_job_list():
    return JobManager.list_server_job_id()


