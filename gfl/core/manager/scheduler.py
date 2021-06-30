import abc

from gfl.conf import GflConf
from gfl.conf.node import GflNode
from gfl.core.data.job import Job
from gfl.core.manager.sql_execute import *
from gfl.net import NetSend, NetFetch, NetReceive, NetBroadcast


class JobScheduler(object):

    def __init__(self, *, node: GflNode, job: Job):
        super(JobScheduler, self).__init__()
        self.node = node
        self.job = job
        self.step = 0

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def status(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

    @abc.abstractmethod
    def is_available(self):
        pass

    @abc.abstractmethod
    def is_running(self):
        pass

    @abc.abstractmethod
    def is_finished(self):
        pass

    def _get_status(self):
        return get_kv(self.job.job_id, "status")

    def _update_status(self, status):
        save_kv(self.job.job_id, KVEntity(key="status", value=status))

    def _get_step(self):
        step = get_kv(self.job.job_id, "step")
        if step is None:
            return 0
        return int(step)

    def _inc_step(self):
        step = self._get_step()
        save_kv(self.job.job_id, KVEntity(key="step", value=str(step + 1)))


class JobAggregateScheduler(JobScheduler):

    def __init__(self, *, node: GflNode, job: Job):
        super(JobAggregateScheduler, self).__init__(node=node, job=job)

    def start(self):
        pass

    def status(self):
        pass

    def stop(self):
        pass

    def is_available(self):
        pass

    def is_running(self):
        pass

    def is_finished(self):
        pass


class JobTrainScheduler(JobScheduler):

    def __init__(self, *, node: GflNode, job: Job):
        super(JobTrainScheduler, self).__init__(node=node, job=job)
        self.__running = False
        self.__available = False

    def start(self):
        self.__running = True
        status = self._get_status()
        if status == "finished":
            return
        if status == "" or status is None:
            self.register()
        if status == "training":
            step = self._get_step()
            self.train(step)
        self.__running = False

    def status(self):
        pass

    def stop(self):
        pass

    def is_available(self):
        return self.__available

    def is_running(self):
        return self.__running

    def is_finished(self):
        pass

    def register(self):
        NetSend.send_cmd_register(self.job.job_id, self.node.address, self.node.pub_key, self.job.dataset.dataset_id)

    def train(self, step):
        trainer_clazz = self.job.job_config.get_trainer()
        trainer = trainer_clazz(job=self.job, step=step, client=self.node)
        trainer.train()
        self._inc_step()
