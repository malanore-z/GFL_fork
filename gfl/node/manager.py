import time
import gfl.core.lfs as lfs
from gfl.conf.node import GflNode
from gfl.core.lfs import load_topology_manager
from gfl.core.manager.job_manager import JobManager
from gfl.core.manager.scheduler import JobAggregateScheduler, JobTrainScheduler


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
        self._is_stop = False

    def run(self):
        while True:
            if self._is_stop is True:
                # ToDo:结束运行时是否需要释放一些资源
                break

            self.listen_job()
            # 为waiting_list中的job构造Scheduler实例，保存到scheduler_list
            while self.waiting_list:
                selected_job = self.waiting_list.pop()

                # 判断是否会重复创建scheduler
                job_is_repeat = False
                for num in range(len(self.scheduler_list) - 1, -1, -1):
                    scheduler = self.scheduler_list[num]
                    if scheduler.job_id == selected_job.job_id:
                        job_is_repeat = True
                        break
                if job_is_repeat is True:
                    continue

                # ToDo：先手动绑定dataset，后面修改
                dataset = lfs.load_dataset("02d418dd05223095b1574e961eb22402")
                selected_job.mount_dataset(dataset)
                temp_topology_manager = load_topology_manager(selected_job.job_id)
                # Todo:根据节点角色来判断当前节点是否参与此job的训练
                print(f"{self.role} {self.node.address} 准备开始执行job{selected_job.job_id}")
                # JobManager.start_job(selected_job.job_id)
                if self.role == "server":
                    scheduler = JobAggregateScheduler(node=self.node, topology_manager=temp_topology_manager,
                                                      job=selected_job)
                    self.scheduler_list.append(scheduler)
                elif self.role == "client":
                    scheduler = JobTrainScheduler(node=self.node, job=selected_job,
                                                  topology_manager=temp_topology_manager)
                    scheduler.register()
                    self.scheduler_list.append(scheduler)
                else:
                    raise ValueError(f"Unsupported role parameter {self.role}")
            # 运行scheduler_list当中的scheduler
            for num in range(len(self.scheduler_list) - 1, -1, -1):
                scheduler = self.scheduler_list[num]
                if scheduler.is_finished():
                    self.scheduler_list.remove(scheduler)
                    print(f"{self.role} {self.node.address} 执行job{scheduler.job_id} 完毕！")
                    JobManager.finish_job(scheduler.job_id)
                else:
                    if scheduler.is_available():
                        print(f"node {self.node.address} 开始执行")
                        scheduler.start()
                        if scheduler.is_finished():
                            self.scheduler_list.remove(scheduler)
                            print(f"{self.role} {self.node.address} 执行job{scheduler.job_id} 完毕！")
                            JobManager.finish_job(scheduler.job_id)

    def listen_job(self):
        # 监听job，并将监听到的job保存到waiting_list中
        # 在单机模式下，所有节点共用一个数据库，所以直接调用此方法获取未完成的job
        jobs = JobManager.unfinished_jobs()
        self.waiting_list = jobs
        # 在多机模式下，各个节点都有各自的数据库
        # 1、调用通信模块的方法监听其余节点发送过来的job
        # 2、将其存储到该节点的数据库当中
        # 3、jobs = JobManager.unfinished_jobs()
        # 4、self.waiting_list = jobs

    def stop(self):
        self._is_stop = True

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
