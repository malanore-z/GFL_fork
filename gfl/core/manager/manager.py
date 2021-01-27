
import json
import time
import uuid

from gfl.conf import GflNode
from gfl.utils import PathUtils


class Manager(object):

    JOB_NAMESPACE = uuid.UUID(GflNode.address[:31] + '1')
    DATASET_NAMESPACE = uuid.UUID(GflNode.address[:31] + "2")

    @classmethod
    def __generate_uuid(cls, namespace):
        nano_time = int(int(1e9) * time.time())
        name = GflNode.address[31:] + str(nano_time / 100)
        return uuid.uuid3(namespace, name).hex.replace("-", "")

    @classmethod
    def generate_job_id(cls):
        return cls.__generate_uuid(cls.JOB_NAMESPACE)

    @classmethod
    def generate_dataset_id(cls):
        return cls.__generate_uuid(cls.DATASET_NAMESPACE)
