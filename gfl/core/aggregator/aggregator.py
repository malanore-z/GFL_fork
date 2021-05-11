import abc
import os
import pickle
import sys

import torch

from gfl.conf.node import GflNode
from gfl.core.context import WorkDirContext
from gfl.core.data import Job
from gfl.core.data.config import AggregateConfig
from gfl.core.lfs.path import JobPath
from gfl.utils import TimeUtils, PathUtils


class Aggregator(object):

    def __init__(self, job: Job, step: int, server: GflNode = GflNode.default_node):
        super(Aggregator, self).__init__()
        self.global_model_param = None
        self.start_time = TimeUtils.millis_time()
        self.job = job
        self.step = step
        self.server = server
        self.job_id = job.job_id
        self._parse_aggregate_config(job.aggregate_config)

    def aggregate(self, client_model_params):
        job_path = JobPath(self.job_id)
        work_dir = job_path.server_work_dir(self.step)
        os.makedirs(work_dir, exist_ok=True)
        with WorkDirContext(work_dir):
            self._pre_aggregate()
            self._aggregate(client_model_params)
            self._post_aggregate()
        return self.global_model_param

    def send(self, data, name, client_addr):
        """send data to target client"""
        print(f"[Job {self.job.job_id}] Aggregator broadcasting {name} to client {client_addr}")
        pickled_data = pickle.dumps(data)
        data_size = sys.getsizeof(pickled_data)
        path_util = JobPath(self.job.job_id)
        client_path = path_util.client_params_dir(self.step, client_addr)
        os.makedirs(client_path, exist_ok=True)
        data_path = client_path + f"/{name}.pkl"
        with open(data_path) as f:
            pickle.dump(pickled_data, f)
        print(
            f"[Job {self.job.job_id}] Aggregator send {round(data_size / 1024 ** 2, 2)} MB of {name} data to client {client_addr}")

    def broadcast(self, data, name, clients=None):
        """broadcast message to all selected clients"""
        print(f"[Job {self.job.job_id}] Aggregator broadcasting {name} to clients")
        pickled_data = pickle.dumps(data)
        data_size = sys.getsizeof(pickled_data)
        path_util = JobPath(self.job.job_id)
        global_path = path_util.global_params_dir(self.step)
        os.makedirs(global_path, exist_ok=True)
        data_path = global_path + f"/{name}.pkl"
        with open(data_path) as f:
            pickle.dump(pickled_data, f)

        print(f"[Job {self.job.job_id}] Aggregator send {round(data_size / 1024**2, 2)} MB of {name} data to all selected clients")

    def _pre_aggregate(self):
        pass

    @abc.abstractmethod
    def extract_weights(self):
        """提取出模型的权重"""

    @abc.abstractmethod
    def _aggregate(self, client_model_params):
        raise NotImplementedError("")

    def _post_aggregate(self):
        pass

    def _parse_aggregate_config(self, aggregate_config: AggregateConfig):
        pass
