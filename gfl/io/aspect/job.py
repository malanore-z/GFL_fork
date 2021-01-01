from pathlib import PurePath

from gfl.conf import GflPath, GflNode
from gfl.io.aspect.inner import *


def load_job(job_id):
    dir = PurePath(GflPath.job_dir, job_id)
    file_ipfs, file_obj = load_dir(dir)
    return {
        "client": GflNode.address,
        "job_id": job_id,
        "file_ipfs": file_ipfs,
        "file_obj": file_obj
    }


def load_server_job(job_id):
    dir = PurePath(GflPath.server_dir, job_id)
    file_ipfs, file_obj = load_dir(dir)
    return {
        "client": GflNode.address,
        "job_id": job_id,
        "file_ipfs": file_ipfs,
        "file_obj": file_obj
    }


