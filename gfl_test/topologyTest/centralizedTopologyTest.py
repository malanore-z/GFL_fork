import unittest

from gfl.conf.node import GflNode
from gfl.core.manager import JobManager
from gfl.core.manager.scheduler import JobTrainScheduler, JobAggregateScheduler
from gfl.core.manager.sql_execute import ClientEntity, save_client
from gfl_test.job.generate_job import generate_job, generate_dataset
from gfl.topology.centralized_topology_manager import CentralizedTopologyManager


class TestMethod(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_start(self):
        # 共有两个训练节点，有一个任务，这个任务需要训练两轮。需要1个aggregator_scheduler，需要2个jobTrainerScheduler
        # 生成dataset-->生成job-->job.mount_dataset-->
        # 1、client生成一个job的情况：
        # client生成一个job之后进行提交、广播
        # server监听到client广播的job之后，调用job.add_server进行绑定，再进行广播。生成scheduler并运行。
        # client收到server广播的job之后。生成scheduler，并运行

        # 2、server生成一个job的情况：
        # server生成一个job之后，调用job.add_server进行绑定，再进行广播。生成scheduler并运行。
        # client收到server广播的job之后。生成scheduler，并运行

        # 生成dataset
        self.dataset = generate_dataset()
        print("生成的dataset_id:" + self.dataset.dataset_id)

        # 生成3个一样的job
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
        # 生成3个node。1个是聚合方，2个是训练方
        GflNode.init_node()
        node1 = GflNode.default_node
        GflNode.init_node()
        node2 = GflNode.default_node
        GflNode.init_node()
        node3 = GflNode.default_node
        # 在正常情况下，server监听到client发送的job之后，会在serve生成一个TopologyManager，并广播
        # 拓扑结构
        self.tpmgr = CentralizedTopologyManager(train_node_num=2, job_id=self.job.job_id)
        self.tpmgr.add_server(server_node=node1, add_into_topology=True)
        # 加到拓扑结构当中
        self.tpmgr.add_node_into_topology(node2)
        self.tpmgr.add_node_into_topology(node3)
        # 生成中心化的拓扑结构
        self.tpmgr.generate_topology()

        # 根据job生成scheduler
        # 聚合方
        self.aggregator_scheduler = JobAggregateScheduler(node=node1, job=self.job, topology_manager=self.tpmgr)
        # 训练方
        self.jobTrainerScheduler_1 = JobTrainScheduler(node=node2, job=self.job_2, topology_manager=self.tpmgr)
        JobManager.init_job_sqlite(self.job_2.job_id)
        client1 = ClientEntity(self.jobTrainerScheduler_1.node.address,
                               self.jobTrainerScheduler_1.job.dataset.dataset_id,
                               self.jobTrainerScheduler_1.node.pub_key)
        save_client(self.job_2.job_id, client=client1)
        self.jobTrainerScheduler_1.register()
        # 训练方
        self.jobTrainerScheduler_2 = JobTrainScheduler(node=node3, job=self.job_3, topology_manager=self.tpmgr)
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
