

class JobScheduler(object):

    def __init__(self, *, node=None):
        super(JobScheduler, self).__init__()


class JobTrainScheduler(JobScheduler):

    def __init__(self):
        super(JobTrainScheduler, self).__init__()


class JobAggregateScheduler(JobScheduler):

    def __init__(self):
        super(JobAggregateScheduler, self).__init__()
