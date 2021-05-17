from gfl.core.manager.scheduler import JobTrainScheduler, JobAggregateScheduler
from gfl.conf.node import GflNode
from gfl.core.manager.job_manager import JobManager
from gfl_test.job.generate_job import generate_job, generate_dataset
from gfl.core.manager.sql_execute import ClientEntity, save_client

import unittest

from gfl_test.model.mnist_model import Net


class TestMethod(unittest.TestCase):

    def setUp(self) -> None:
        # 共有两个训练节点，有一个任务，这个任务需要训练两轮。需要1个aggregator_scheduler，需要2个jobTrainerScheduler
        # 将这3个调度器放入队列
        # 队列非空时，从队列中取出第一个调度器，判断是否可以开始执行。
        # 可以执行，则执行。执行完毕之后，判断是否达到任务的要求（训练是否到达了指定轮数）
        # 没有达到任务的要求，则放入队尾
        # 不可以执行，则放入队尾
        self.dataset = generate_dataset()
        print("生成的dataset_id:" + self.dataset.dataset_id)
        self.job = generate_job()
        print("生成的job_id:" + self.job.job_id)
        self.job.mount_dataset(self.dataset)

        self.job_2 = generate_job()
        self.job_2.job_id = self.job.job_id
        self.job_2.mount_dataset(self.dataset)
        print("生成的job_2_id:" + self.job_2.job_id)

        self.job_3 = generate_job()
        self.job_3.job_id = self.job.job_id
        self.job_3.mount_dataset(self.dataset)
        print("生成的job_3_id:" + self.job_3.job_id)

        GflNode.init_node()
        node1 = GflNode.default_node
        self.aggregator_scheduler = JobAggregateScheduler(node=None, job=self.job)

        self.jobTrainerScheduler_1 = JobTrainScheduler(node=node1, job=self.job_2)
        JobManager.init_job_sqlite(self.job_2.job_id)
        client1 = ClientEntity(self.jobTrainerScheduler_1.node.address,
                               self.jobTrainerScheduler_1.job.dataset.dataset_id,
                               self.jobTrainerScheduler_1.node.pub_key)
        save_client(self.job_2.job_id, client=client1)
        self.jobTrainerScheduler_1.register()

        GflNode.init_node()
        node2 = GflNode.default_node
        self.jobTrainerScheduler_2 = JobTrainScheduler(node=node2, job=self.job_3)
        client2 = ClientEntity(self.jobTrainerScheduler_2.node.address,
                               self.jobTrainerScheduler_2.job.dataset.dataset_id,
                               self.jobTrainerScheduler_2.node.pub_key)
        save_client(self.job_3.job_id, client=client2)
        self.jobTrainerScheduler_2.register()

        # 将调度器放入队列
        self.list = []
        self.list.append(self.aggregator_scheduler)
        self.list.append(self.jobTrainerScheduler_1)
        self.list.append(self.jobTrainerScheduler_2)

    def test_start(self):
        # 当队列非空时，遍历整个队列，判断当前调度器是否可以运行
        # while(){
        #     for(){
        #           is_available()
        #           aggregate_scheduler.status() != JobStatus.ALL_FINISHED
        #     }
        # }
        while len(self.list) != 0:
            for num in range(len(self.list) - 1, -1, -1):
                scheduler = self.list[num]
                if scheduler.is_finished():
                    self.list.remove(scheduler)
                else:
                    if scheduler.is_available():
                        scheduler.start()
                        if scheduler.is_finished():
                            self.list.remove(scheduler)


if __name__ == "__main__":
    unittest.main()
