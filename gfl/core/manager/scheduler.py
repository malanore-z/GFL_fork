import abc

from gfl.conf import GflConf
from gfl.conf.node import GflNode


class JobScheduler(object):

    def __init__(self, *, node, job):
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


class JobAggregateScheduler(JobScheduler):

    def __init__(self, *, node, job):
        super(JobAggregateScheduler, self).__init__(node=node, job=job)

    def start(self):
        pass

    def status(self):
        pass

    def stop(self):
        pass


class JobTrainScheduler(JobScheduler):

    def __init__(self, node, job):
        super(JobTrainScheduler, self).__init__(node=node, job=job)

    def start(self):
        pass

    def status(self):
        pass

    def stop(self):
        pass

    def register(self):
        pass

    def train(self, step):
        trainer_clazz = self.job.job_config.get_trainer()
        trainer = trainer_clazz(job=self.job, step=0, client=self.node)
        trainer.train()
