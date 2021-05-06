import torch
import os

import gfl_test
from gfl.core.lfs.path import JobPath

from gfl.core.manager.generator import JobGenerator
from gfl.core.manager.scheduler import JobTrainScheduler, JobAggregateScheduler
from gfl.conf.node import GflNode
from gfl.core.data.job import Job
from gfl.core.manager.job_manager import JobManager
from gfl.utils import PathUtils
from gfl_test.job.generate_job import generate_job, generate_dataset
from gfl.core.manager.job_status import JobStatus
from gfl.net.standlone import cache
from gfl.core.manager.sql_execute import ClientEntity, save_client
import copy

import unittest

from gfl_test.model.mnist_model import Net


class TestMethod(unittest.TestCase):

    def setUp(self) -> None:
        self.dataset = generate_dataset()
        print("dataset_id:" + self.dataset.dataset_id)
        self.job = generate_job()
        print("job_id:" + self.job.job_id)
        self.job.mount_dataset(self.dataset)
        GflNode.init_node()
        node = GflNode.default_node
        self.aggregator_scheduler = JobAggregateScheduler(node=None, job=copy.deepcopy(self.job), target_num=1)
        self.jobTrainerScheduler = JobTrainScheduler(node=node, job=copy.deepcopy(self.job))
        JobManager.init_job_sqlite(self.job.job_id)
        client = ClientEntity(self.jobTrainerScheduler.node.address, self.jobTrainerScheduler.job.dataset.dataset_id,
                              self.jobTrainerScheduler.node.pub_key)
        save_client(self.job.job_id, client=client)

    def test_start(self):
        if self.jobTrainerScheduler.is_available():
            self.jobTrainerScheduler.start()
            print(self.jobTrainerScheduler.status())
        if self.aggregator_scheduler.is_available():
            print("开始模型聚合")
            self.aggregator_scheduler.start()
            print("完成模型聚合")


if __name__ == "__main__":
    unittest.main()
