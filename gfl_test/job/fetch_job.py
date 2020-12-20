import gfl_test

from gfl.core.manager import JobManager


job_id = "844508dca05f31dbbd48d3af559c5576"
dataset_id = "51e76345464f3834abf10db50c103b1f"


if __name__ == "__main__":
    JobManager.fetch_job(job_id, dataset_id)