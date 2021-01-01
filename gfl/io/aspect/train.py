

from pathlib import PurePath

from gfl.conf import GflPath, GflNode
from gfl.io.aspect.inner import *


def load_params(job_id, step):
    dir = PurePath(GflPath.client_dir, job_id, step)
    file_ipfs, file_obj = load_dir(dir=dir)
    return {
        "job_id": job_id,
        "client": GflNode.address,
        "step": step,
        "file_ipfs": file_ipfs,
        "file_obj": file_obj
    }


def send_validation_result(job_id, step, result):
    return {
        "job_id": job_id,
        "client": GflNode.address,
        "step": step,
        "result": result
    }
