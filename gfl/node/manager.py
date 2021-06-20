import time
import sys
import gfl_test.dataset as fl_dataset
import gfl_test.model as fl_model
import gfl.core.lfs as lfs
from gfl.conf import GflConf
from gfl.conf.node import GflNode
from gfl.core.manager.job_manager import JobManager
from gfl.core.manager.generator import DatasetGenerator, JobGenerator
from gfl.core.manager.scheduler import JobAggregateScheduler, JobTrainScheduler
from gfl.topology.centralized_topology_manager import CentralizedTopologyManager
from gfl_test.job.generate_job import generate_job, generate_dataset
from gfl.core.manager.sql_execute import ClientEntity, save_client


class NodeManager(object):

    def __init__(self, *, node: GflNode = None, role: str = "client"):
        super(NodeManager, self).__init__()
        self.node = GflNode.default_node if node is None else node
        self.role = role
        self.waiting_list = None
        self.tpmgr = None
        self.scheduler_list = []
        # TODO: 为了测试使用，之后需要删除
        self.server_node = None

    def run(self):
        # 一直运行，不断地从队列中获取可以运行的任务并执行任务
        # 1. 使用 JobManager 加载未完成的job
        # 2. 根据配置参数决定是否继续训练未完成的job
        # 3. 对需要训练的job， 构造JobScheduler实例，并将其注册到任务调度器中，此JobScheduler的控制 权移交任务调度器。
        # 4. 开始监听网络中新的job。
        self.listen_job()
        while self.waiting_list:
            selected_job = self.waiting_list.pop()
            selected_job.add_server(self.server_node)
            print(f"{self.role} {self.node.address} 开始执行job{selected_job.job_id}")
            # 目前先手动设置dataset
            dataset = lfs.load_dataset("76ffe215beaf3180ab970219f18915c2")
            selected_job.mount_dataset(dataset)
            # 目前先手动设置拓扑结构
            if self.role == "server":
                scheduler = JobAggregateScheduler(node=self.node, topology_manager=self.tpmgr, job=selected_job)
                while not scheduler.is_finished():
                    if scheduler.is_available():
                        scheduler.start()
                    else:
                        time.sleep(10)
                JobManager.finish_job(selected_job.job_id)
            elif self.role == "client":
                scheduler = JobTrainScheduler(node=self.node, job=selected_job, topology_manager=self.tpmgr)
                client = ClientEntity(scheduler.node.address,
                                      scheduler.job.dataset.dataset_id,
                                      scheduler.node.pub_key)
                save_client(selected_job.job_id, client=client)
                scheduler.register()
                scheduler = JobTrainScheduler(node=self.node, job=selected_job, topology_manager=self.tpmgr)
                while not scheduler.is_finished():
                    if scheduler.is_available():
                        print("开始执行")
                        scheduler.start()
                    else:
                        print("等待")
                        time.sleep(10)
            else:
                raise ValueError(f"Unsupported role parameter {self.role}")

    def listen_job(self):
        # 监听用户新生成的job
        # server: 广播job
        # client: 监听server广播的job
        jobs = JobManager.unfinished_jobs()
        self.waiting_list = jobs

    def submit_job(self, job):
        # 提交任务，将任务信息记录到数据库
        # server: 广播job
        JobManager.submit_job(job)

    def start_job(self, job_id):
        # 将任务加入到运行队列
        pass

    def cancle_job(self, job_id):
        # 取消任务，并更改数据库中的状态
        JobManager.cancle_job(job_id=job_id)

    def delay_job(self, job_id):
        # 将某个进行/排队中的任务延后
        pass

    def stop(self):
        # 暂停manager的运行
        pass
