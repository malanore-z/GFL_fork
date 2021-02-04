
from gfl.core.data import Job
from gfl.utils import TimeUtils


class Aggregator(object):

    def __init__(self, job: Job):
        super(Aggregator, self).__init__()
        self.start_time = TimeUtils.millis_time()
        self.job_id = job.job_id

    def aggregate(self):
        pass

