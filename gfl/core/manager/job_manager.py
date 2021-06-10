import os

import gfl.core.lfs as lfs
from gfl.conf.node import GflNode
from gfl.core.data import Job
from gfl.core.manager.manager import Manager
from gfl.core.manager.scheduler import JobTrainScheduler, JobAggregateScheduler
from gfl.core.manager.sql_execute import *
from gfl.net import NetBroadcast
from gfl.topology.centralized_topology_manager import CentralizedTopologyManager


class JobManager(Manager):
    def __init__(self):
        super().__init__()
        # 维护一个scheduler的队列
        self.scheduler_list = []
        self.node = GflNode.default_node

    def listen_job(self):
        # server：通过此方法监听client新生成的job，记录到数据库
        #         拿到job之后，server还需要采用上帝视角的方式生成topology_manager。实例化topology_manager时需要3个参数：job、n、aggregate_node（topology_manager有两种生成方式：1、直接有一个上帝视角，生成topology_manager；2、边广播job边生成）
        #         还需要调用topology_manager的方法，将client_node添加进拓扑
        #         将topology_manager添加到job当中
        #         广播job
        #         返回这个job
        # client：通过此方法监听server广播的job，记录到数据库，返回job
        # =========================================================
        # 这应该是监听到的,通信模块完成之后需要修改#############
        job = Job()
        if job is not None:
            # 这个job中还没有初始化拓扑结构
            if job.topology_manager is None:
                n = job.aggregate_config.get_clients_per_round()
                for server in job.server_list:
                    if self.node.address == server.address:
                        temp_topology_manager = CentralizedTopologyManager(train_node_num=n, aggregate_node=self.node)
                        # server将client_node添加进拓扑###########
                        # temp_topology_manager.add_node_into_topology()
                        temp_topology_manager.generate_topology()
                        job.mount_topology_manager(temp_topology_manager)
                        break
            JobManager.save_job(job)
        return job

    def cancel_job(self, job_id):
        # 取消任务，并更改数据库中的状态
        pass

    def delay_job(self, job_id):
        # 将某个进行/排队中的任务延后
        pass

    def run(self):
        # 作为入口
        # 一直运行，不断地从队列中获取可以运行的job并执行job。内部调用listen_job（run和listen_job方法重复了）
        # 1. 使用 JobManager 加载未完成的job
        # 2. 根据配置参数决定是否继续训练未完成的job
        # 3. 对需要训练的job， 构造JobScheduler实例，并将其注册到任务调度器中，此JobScheduler的控制 权移交任务调度器。
        # 4. 开始监听网络中新的job。

        # 作为入口。是一个一直运行的死循环
        # 1、调用listen_job获取监听到的job
        # 2、根据job中的信息，实例化对应的scheduler，并将scheduler加入到队列当中
        # 3、运行一轮队列当中的scheduler
        while True:
            job = self.listen_job()
            if job is not None:
                # 实例化scheduler
                is_server = False
                for server in job.server_list:
                    if self.node.address == server.address:
                        is_server = True
                        break
                if is_server is True:
                    scheduler = JobAggregateScheduler(node=self.node, job=job)
                else:
                    scheduler = JobTrainScheduler(node=self.node, job=job)
                    JobManager.init_job_sqlite(job.job_id)
                    client = ClientEntity(scheduler.node.address,
                                          scheduler.job.dataset.dataset_id,
                                          scheduler.node.pub_key)
                    save_client(job.job_id, client=client)
                    scheduler.register()
                self.scheduler_list.append(scheduler)
            # 运行一轮队列当中的scheduler
            for num in range(len(self.scheduler_list) - 1, -1, -1):
                scheduler = self.scheduler_list[num]
                if scheduler.is_finished():
                    self.scheduler_list.remove(scheduler)
                else:
                    if scheduler.is_available():
                        scheduler.start()
                        if scheduler.is_finished():
                            self.scheduler_list.remove(scheduler)

    def stop(self):
        # 停止GFL的运行
        pass

    @classmethod
    def submit_job(cls, job):
        # 1、节点提交job，将job信息记录到数据库
        # 2、并将这个job广播出去
        # server直接调用submit_job方法可以提交任务并广播任务。
        lfs.save_job(job)
        job_file = lfs.load_job_zip(job.job_id)
        NetBroadcast.broadcast_job(job.job_id, job_file)

    @classmethod
    def save_job(cls, job):
        lfs.save_job(job)

    @classmethod
    def unfinished_jobs(cls):
        lfs_jobs = lfs.load_all_job()
        jobs = []
        for job in lfs_jobs:
            status = get_kv(job.job_id, "status")
            if status != "finish":
                jobs.append(job)
        return jobs

    @classmethod
    def init_job_sqlite(cls, job_id):
        create_tables(job_id)
