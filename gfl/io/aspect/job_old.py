

import os
from io import BytesIO
from pathlib import PurePath

from gfl.conf import GflPath, GflConf
from gfl.core.job import ServerJob, ClientJob
from gfl.utils import ZipUtils


def __load_job_dir(job_dir):
    bytes_file = BytesIO()
    ZipUtils.compresss(job_dir, bytes_file, basename="")
    bytes_file.seek(0)
    job = bytes_file.read()
    job_ipfs = None
    if GflConf.ipfs.enabled:
        pass
    return job_ipfs, job


def __store_job_dir(job_dir, job_ipfs, job):
    if job_ipfs is not None:
        pass
    bytes_file = BytesIO(job)
    ZipUtils.extract(bytes_file, job_dir)


def load_job(job_id):
    source_path = PurePath(GflPath.job_dir, job_id).as_posix()
    job_ipfs, job = __load_job_dir(source_path)
    return job_id, job_ipfs, job


def store_server_job(job_id: str, job_ipfs:str=None, job:bytes=None):
    target_path = PurePath(GflPath.server_dir, job_id).as_posix()
    __store_job_dir(target_path, job_ipfs, job)
    server_job = ServerJob(job_id)
    server_job.init_sqlite()


def load_server_job(job_id: str):
    source_path = PurePath(GflPath.server_dir, job_id).as_posix()
    job_ipfs, job = __load_job_dir(source_path)
    return job_id, job_ipfs, job


def store_client_job(job_id: str, job_ipfs:str=None, job:bytes=None):
    target_path = PurePath(GflPath.client_dir, job_id).as_posix()
    __store_job_dir(target_path, job_ipfs, job)
    client_job = ClientJob(job_id)
    client_job.init_sqlite()


def register_client(job_id: str, client: str):
    server_job = ServerJob(job_id)
    server_job.register_client(client)
