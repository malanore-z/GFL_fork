import time
import uuid

from gfl.conf.node import GflNode
from gfl.core.manager.job_manager import JobManager


class Manager(object):
    def __init__(self):
        """
        根据节点信息进行初始化操作
        """
        pass

    def listen_job(self):
        # 监听用户新生成的job
        # client: 将job发送给server
        # server: 广播job
        # client: 监听server广播的job
        pass

    def submit_job(self, job):
        # 提交任务，将任务信息记录到数据库
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

    def run(self):
        # 一直运行，不断地从队列中获取可以运行的任务并执行任务
        # 1. 使用 JobManager 加载未完成的job
        # 2. 根据配置参数决定是否继续训练未完成的job
        # 3. 对需要训练的job， 构造JobScheduler实例，并将其注册到任务调度器中，此JobScheduler的控制 权移交任务调度器。
        # 4. 开始监听网络中新的job。
        pass

    def stop(self):
        # 暂停manager的运行
        pass