import time
import sys

from gfl.conf import GflConf
import gfl.core.lfs as lfs
from gfl.conf.node import GflNode
from gfl.core.lfs import load_topology_manager
from gfl.core.manager.node_manager import JobManager
from gfl.core.manager.scheduler import JobAggregateScheduler, JobTrainScheduler
from gfl.core.manager.sql_execute import ClientEntity, save_client


# 发布job和运行job的过程：
# 1、任意一个节点都可以新建一个job,按序进行初始化、广播、运行直至job达到结束条件
#   1.1 新建一个job，设置模型、数据、聚合参数、训练参数等，并且需要通过配置文件的方式（也可以调用相关的方法）生成与这个job相关联的topology_manager
#   1.2 调用init_job_sqlite、submit_job完成初始化操作，并且进行广播，并在数据库中甚至为waiting状态，等待接下来运行
#   1.3 运行job（何时创建scheduler？）
# 2、其余节点监听到此job之后，进行初始化操作。在运行这个job获取job和topology_manager。根据这个job与本节点是否有关，保存在本地。并创建对应的scheduler


class NodeManager(object):

    def __init__(self, *, node: GflNode = None, role: str = "client"):
        super(NodeManager, self).__init__()
        self.node = GflNode.default_node if node is None else node
        self.role = role

        self.waiting_list = None
        self.tpmgr = None
        self.scheduler_list = []

    def run(self):
        # 一直运行，不断地从队列中获取可以运行的任务并执行任务
        # 1. 使用 JobManager 加载未完成的job
        # 2. 根据配置参数决定是否继续训练未完成的job
        # 3. 对需要训练的job， 构造JobScheduler实例，并将其注册到任务调度器中，此JobScheduler的控制 权移交任务调度器。
        # 4. 开始监听网络中新的job。
        self.listen_job()
        print(f"{self.node.address} waiting_list:{self.waiting_list}")
        while self.waiting_list:
            selected_job = self.waiting_list.pop()
            print(f"{self.role} {self.node.address} 开始执行job{selected_job.job_id}")
            # 目前先手动设置dataset
            dataset = lfs.load_dataset("76ffe215beaf3180ab970219f18915c2")
            selected_job.mount_dataset(dataset)
            tpmgr = load_topology_manager(selected_job.job_id)
            if self.role == "server":
                scheduler = JobAggregateScheduler(node=self.node, job=selected_job, topology_manager=tpmgr)
                while not scheduler.is_finished():
                    if scheduler.is_available():
                        print(f"server {self.node.address} 开始执行")
                        scheduler.start()
                    else:
                        print(f"server {self.node.address} 等待")
                        time.sleep(10)
                JobManager.finish_job(selected_job.job_id)
            elif self.role == "client":
                scheduler = JobTrainScheduler(node=self.node, job=selected_job, topology_manager=tpmgr)
                client = ClientEntity(scheduler.node.address,
                                      scheduler.job.dataset.dataset_id,
                                      scheduler.node.pub_key)
                save_client(selected_job.job_id, client=client)
                scheduler.register()
                scheduler = JobTrainScheduler(node=self.node, job=selected_job, topology_manager=tpmgr)
                while not scheduler.is_finished():
                    if scheduler.is_available():
                        print(f"client {self.node.address} 开始执行")
                        scheduler.start()
                    else:
                        print(f"client {self.node.address} 等待")
                        time.sleep(10)
            else:
                raise ValueError(f"Unsupported role parameter {self.role}")

    def listen_job(self):
        # 监听其他节点新生成的job
        # 在单机模式下，所有节点共用一个数据库，所以直接调用此方法获取未完成的job
        jobs = JobManager.unfinished_jobs()
        self.waiting_list = jobs
        # 在多机模式下，各个节点都有各自的数据库
        # 1、调用通信模块的方法监听其余节点发送过来的job
        # 2、将其存储到该节点的数据库当中
        # 3、jobs = JobManager.unfinished_jobs()
        # 4、self.waiting_list = jobs
        # 问题：是否需要去查询job的server列表和client列表，从而判断这个job是否与当前节点有关

    def submit_job(self, job):
        # 提交任务，将任务信息记录到数据库，并广播job
        JobManager.submit_job(job)

    def cancel_job(self, job_id):
        # 取消任务，并更改数据库中的状态
        JobManager.cancel_job(job_id=job_id)

    def delay_job(self, job_id):
        # 将某个进行/排队中的任务延后
        pass

    def stop(self):
        # 暂停manager的运行
        pass
