import torch
import os

from gfl.core.lfs.path import JobPath

from gfl.core import JobTrainScheduler
from gfl.core.manager.node import GflNode
from gfl.utils import PathUtils
from tests.gfl_test.job.generate_job import generate_job, generate_dataset

import unittest

from tests.gfl_test.model.mnist_model import Net


class TestMethod(unittest.TestCase):

    def setUp(self) -> None:
        self.dataset = generate_dataset()
        print("dataset_id:" + self.dataset.dataset_id)
        self.job = generate_job()
        print("job_id:" + self.job.job_id)
        self.job.mount_dataset(self.dataset)
        GflNode.init_node()
        node = GflNode.default_node
        self.jobTrainerScheduler = JobTrainScheduler(node=node, job=self.job)
        self.jobTrainerScheduler.register()

        # aggregator需要初始化随机模型
        global_params_dir = JobPath(self.job.job_id).global_params_dir(self.job.cur_round)
        # print("global_params_dir:"+global_params_dir)
        os.makedirs(global_params_dir, exist_ok=True)
        model_params_path = PathUtils.join(global_params_dir, self.job.job_id + '.pth')
        # print("model_params_path:"+model_params_path)
        model = Net()
        torch.save(model.state_dict(), model_params_path)

    # def test_init_(self):
    #     self.assertEqual(self.jobTrainerScheduler.status(), JobStatus.RESOURCE_NOT_ALREADY)

    # def test_get_model_params_path(self):
    #     print(self.jobTrainerScheduler.get_model_params_path(job_id=self.job.job_id, job_round=self.job.cur_round))
    #     print(self.jobTrainerScheduler.status())

    # def test_is_available(self):
    #     print(self.jobTrainerScheduler.is_available())  # True

    def test_start(self):
        if self.jobTrainerScheduler.is_available():
            self.jobTrainerScheduler.start()
            print(self.jobTrainerScheduler.status())


if __name__ == "__main__":
    unittest.main()
