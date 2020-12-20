import gfl_test

import os
import json
from pathlib import PurePath

from gfl.core.manager import JobManager
from gfl.core.trainer import SupervisedTrainer

job_id = "844508dca05f31dbbd48d3af559c5576"


if __name__ == "__main__":
    job = JobManager.load_client_job(job_id)
    trainer = SupervisedTrainer(job)
    trainer.train()
    pass