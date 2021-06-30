import time
import gfl.core.lfs as lfs
from gfl.conf.node import GflNode
from gfl.core.lfs import load_topology_manager
from gfl.core.manager.job_manager import JobManager
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
        self.scheduler_list = []

    def run(self):
        # 只测试了单个任务的情况，run方法不是一个无限循环
        # while True:
        # 监听job，并将监听到的job保存到waiting_list中
        self.listen_job()
        # 为waiting_list中的job构造Scheduler实例，保存到scheduler_list
        while self.waiting_list:
            selected_job = self.waiting_list.pop()
            print(f"{self.role} {self.node.address} 准备开始执行job{selected_job.job_id}")
            # JobManager.start_job(selected_job.job_id)
            # 目前先手动设置dataset
            dataset = lfs.load_dataset("02d418dd05223095b1574e961eb22402")
            # 如果是server应该不需要这一步?
            selected_job.mount_dataset(dataset)
            temp_topology_manager = load_topology_manager(selected_job.job_id)
            if self.role == "server":
                scheduler = JobAggregateScheduler(node=self.node, topology_manager=temp_topology_manager,
                                                  job=selected_job)
                self.scheduler_list.append(scheduler)
            elif self.role == "client":
                scheduler = JobTrainScheduler(node=self.node, job=selected_job,
                                              topology_manager=temp_topology_manager)
                client = ClientEntity(scheduler.node.address,
                                      scheduler.job.dataset.dataset_id,
                                      scheduler.node.pub_key)
                save_client(selected_job.job_id, client=client)
                scheduler.register()
                self.scheduler_list.append(scheduler)
            else:
                raise ValueError(f"Unsupported role parameter {self.role}")
        # 运行1轮scheduler_list当中的scheduler
        while len(self.scheduler_list) != 0:
            for num in range(len(self.scheduler_list) - 1, -1, -1):
                scheduler = self.scheduler_list[num]
                if scheduler.is_finished():
                    self.scheduler_list.remove(scheduler)
                    JobManager.finish_job(scheduler.job_id)
                else:
                    if scheduler.is_available():
                        print(f"client {self.node.address} 开始执行")
                        scheduler.start()
                        if scheduler.is_finished():
                            self.scheduler_list.remove(scheduler)
                            JobManager.finish_job(scheduler.job_id)

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

    def stop(self):
        # 暂停manager的运行
        pass

    def submit_job(self, job):
        # 提交任务，将任务信息记录到数据库，并广播job
        JobManager.submit_job(job)

    def cancel_job(self, job_id):
        # 取消任务，并更改数据库中的状态
        JobManager.cancel_job(job_id=job_id)

    def delay_job(self, job_id):
        # 将某个进行/排队中的任务延后
        pass

    def start_job(self, job_id):
        # 将任务加入到运行队列
        pass
