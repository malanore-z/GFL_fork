import torch
from gfl.core.data import Job
from gfl.utils import TimeUtils


class Aggregator(object):

    def __init__(self, job: Job):
        super(Aggregator, self).__init__()
        self.start_time = TimeUtils.millis_time()
        self.job_id = job.job_id
        self.global_param = None

    def aggregate(self, client_model_params):
        pass

    def export_model(self, path):
        torch.save(self.global_model_param, path)