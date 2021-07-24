import abc
import os

from gfl.core.data import Job
from gfl.core.lfs import JobPath
from gfl.core.manager.node import GflNode
from gfl.core.scheduler.job_status import JobStatus


class JobExecutor(object):

    def __init__(self, *, node: GflNode, job: Job):
        super(JobExecutor, self).__init__()
        self.node = node
        self.job = job

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


class JobTrainExecutor(JobExecutor):

    def __init__(self, *, node: GflNode, job: Job, step: int):
        super(JobTrainExecutor, self).__init__(node=node, job=job)
        self.trainer = None
        self.step = step
        self.__status = JobStatus.RESOURCE_NOT_ALREADY

    def init_trainer(self):
        self.job.job_config.trainer.is_instance = True
        trainer_clazz = self.job.job_config.get_trainer()
        self.trainer = trainer_clazz(job=self.job, step=self.step, client=self.node)

    def make_dirs(self):
        cur_round = self.job.cur_round
        client_params_dir = JobPath(self.job.job_id).client_params_dir(cur_round, self.node.address)
        os.makedirs(client_params_dir, exist_ok=True)

    def train(self):
        pass

    def start(self):
        """

        :return:
        """
        self.make_dirs()
        self.train()
        self.job.cur_round += 1
        return self.is_finished()

    def status(self):
        return self.__status

    def stop(self):
        pass

    def is_available(self):
        pass

    def is_running(self):
        pass

    def is_finished(self):
        pass


class JobAggregateExecutor(JobExecutor):

    def __init__(self, *, node: GflNode, job: Job):
        super(JobAggregateExecutor, self).__init__(node=node, job=job)

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
