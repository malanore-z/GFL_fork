import os
import time
from pathlib import PurePath

import torch

import gfl
from gfl.conf import GflPath
from gfl.core.entity.config import AggregateConfig, TrainConfig
from gfl.core.context import WorkDirContext
from gfl.core.old_job import ServerJob


class Aggregator(object):

    def __init__(self, job: ServerJob):
        super(Aggregator, self).__init__()
        self.start_time = time.time()
        self.job = job
        self._parse_train_config(job.train_config)
        self._parse_aggregate_config(job.aggregate_config)

    def aggregate(self):
        workdir = PurePath(GflPath.server_work_dir, self.job.job_id, self.job.current_step())
        os.makedirs(workdir, exist_ok=True)
        self._load_client_parameters()
        with WorkDirContext(workdir):
            params = self._aggregate()
        self._save_aggregate_parameters(params)

    def _parse_train_config(self, train_config: TrainConfig):
        pass

    def _parse_aggregate_config(self, aggregate_config: AggregateConfig):
        pass

    def _load_client_parameters(self):
        params_dir = PurePath(GflPath.server_dir, self.job.job_id, "round-%d" % self.job.current_step()).as_posix()
        if not os.path.exists(params_dir):
            return []
        ret = []
        for client_address in os.listdir(params_dir):
            params_path = PurePath(params_dir, client_address, "client.params").as_posix()
            params = torch.load(params_path, map_location=gfl.device())
            ret.append(params)
        self.client_parameters = ret
        return ret

    def _save_aggregate_parameters(self, params):
        params_path = PurePath(GflPath.server_dir,
                               self.job.job_id,
                               "round-%d" % self.job.current_step(),
                               "aggregate.params").as_posix()
        torch.save(params, params_path)

    def _aggregate(self):
        pass


class FedAvgAggregator(Aggregator):

    def _aggregate(self):
        avg_params = self.client_parameters[0]
        for key in avg_params.keys():
            for i in range(1, len(self.client_parameters)):
                avg_params[key] += self.client_parameters[i][key]
            avg_params[key] = torch.div(avg_params[key], len(self.client_parameters))
        return avg_params

