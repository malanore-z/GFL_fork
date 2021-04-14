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
        n_models = len(client_model_params)
        averaged_param = client_model_params[0]
        weight = 1 / n_models
        for key in averaged_param.keys():
            for idx, client_model_param in enumerate(client_model_params):
                if idx ==0:
                    averaged_param[key] *= weight
                if idx != 0:
                    averaged_param[key] += (client_model_param[key] * weight)
        self.global_model_param = averaged_param

    def export_model(self, path):
        torch.save(self.global_model_param, path)