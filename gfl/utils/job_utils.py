import time
import uuid

from gfl.conf import node_id


class JobUtils(object):

    JOB_NAMESPACE = uuid.UUID(node_id[:31] + '1')
    DATASET_NAMESPACE = uuid.UUID(node_id[:31] + "2")

    def __init__(self):
        super(JobUtils, self).__init__()

    @classmethod
    def generate_job_id(cls):
        return cls.__generate_uuid(cls.JOB_NAMESPACE)

    @classmethod
    def generate_dataset_id(cls):
        return cls.__generate_uuid(cls.DATASET_NAMESPACE)

    @classmethod
    def __generate_uuid(cls, namespace):
        nano_time = int(int(1e9) * time.time())
        name = node_id[31:] + str(nano_time / 100)
        return uuid.uuid3(namespace, name).hex.replace("-", "")
