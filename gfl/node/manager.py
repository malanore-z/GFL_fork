import time
import sys

from gfl.conf import GflConf
from gfl.conf.node import GflNode
from gfl.core.manager.job_manager import JobManager


class NodeManager(object):

    def __init__(self, *, node: GflNode = None, role: str = "client"):
        super(NodeManager, self).__init__()
        self.node = GflNode.default_node if node is None else node
        self.role = role

    def run(self):
        jobs = JobManager.unfinished_jobs()
        self.listen_job()
        pass

    def listen_job(self):
        pass
