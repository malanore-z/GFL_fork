from gfl.core.data.config import TrainConfig, AggregateConfig, JobConfig
from gfl.core.data.dataset import Dataset
from gfl.core.data.metadata import JobMetadata
from gfl.topology.base_topology_manager import BaseTopologyManager


class Job(object):

    def __init__(self, *,
                 job_id: str = None,
                 metadata: JobMetadata = None,
                 job_config: JobConfig = None,
                 train_config: TrainConfig = None,
                 aggregate_config: AggregateConfig = None):
        super(Job, self).__init__()
        self.module = None
        self.job_id = job_id
        self.cur_round = 0
        self.metadata = metadata
        self.job_config = job_config
        self.train_config = train_config
        self.aggregate_config = aggregate_config
        self.dataset = None
        self.topology_manager = None
        self.server_address_list = []

    def mount_dataset(self, dataset: Dataset):
        self.dataset = dataset

    def mount_topology_manager(self, topology_manager: BaseTopologyManager):
        self.topology_manager = topology_manager

    def add_server(self, server_node):
        self.server_address_list.append(server_node.address)
