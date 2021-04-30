import abc
import os

from gfl.conf.node import GflNode
from gfl.core.context import WorkDirContext
from gfl.core.data import Job
from gfl.core.data.config import AggregateConfig
from gfl.core.lfs.path import JobPath
from gfl.utils import TimeUtils


class Aggregator(object):

    def __init__(self, job: Job, step: int, server: GflNode = GflNode.default_node):
        super(Aggregator, self).__init__()
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

    def _pre_aggregate(self):
        pass

    @abc.abstractmethod
    def _aggregate(self, client_model_params):
        raise NotImplementedError("")

    def _post_aggregate(self):
        pass

    def _parse_aggregate_config(self, aggregate_config: AggregateConfig):
        pass
