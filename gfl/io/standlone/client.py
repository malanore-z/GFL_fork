import os
import time
from pathlib import PurePath

import gfl.io.aspect as aspect
import gfl.io.standlone.server as server
from gfl.conf import GflPath, GflNode


@aspect.Aspect(aspect.load_job, position="before")
def send_published_job(job_id, job_ipfs, job):
    if job_ipfs is not None:
        pass
    server.receive_published_job(job_id, job_ipfs, job)


def register(job_id: str):
    server.register_client(job_id, GflNode.address)


@aspect.Aspect(aspect.store_client_job)
def fetch_server_job(job_id: str):
    server.broadcast_server_job(job_id)


def fetch_server_jobid_list():
    return server.server_job_list()

