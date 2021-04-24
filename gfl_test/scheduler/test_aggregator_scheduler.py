import time
from gfl.core.manager.scheduler import JobAggregateScheduler
from gfl.core.data.job import Job
from gfl_test.job.generate_job import generate_job


class TestAggregatorScheduler:
    def setup(self):
        self.job = generate_job()
        self.aggregator_scheduler = JobAggregateScheduler(node=None, job=self.job)

    def test_fit(self):
        while not self.aggregator_scheduler.is_available():
            time.sleep(100)
        self.aggregator_scheduler.aggregate()