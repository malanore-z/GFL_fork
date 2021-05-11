import time
from gfl.core.manager.aggregate_scheduler import JobAggregateScheduler
from gfl.core.data.job import Job
from gfl_test.job.generate_job import generate_job


class TestAggregatorScheduler:
    def setup(self):
        self.job = generate_job()
        self.job.job_id = "387ffff589963653921173bdfa54a417"
        self.aggregator_scheduler = JobAggregateScheduler(node=None, job=self.job, target_num=1)

    def test_fit(self):
        # while not self.aggregator_scheduler.is_available():
        #     time.sleep(100)
        # self.aggregator_scheduler.aggregate()
        pass


if __name__ == '__main__':
    test = TestAggregatorScheduler()
    test.setup()
    print(test.aggregator_scheduler.is_available())