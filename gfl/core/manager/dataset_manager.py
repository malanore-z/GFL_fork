
import gfl.core.lfs as lfs
from gfl.conf.node import GflNode
from gfl.core.data import Dataset, DatasetMetadata
from gfl.core.data.config import DatasetConfig
from gfl.core.manager.manager import Manager
from gfl.net import NetBroadcast


class DatasetManager(Manager):

    @classmethod
    def generate_dataset(cls, module,
                         metadata: DatasetMetadata,
                         dataset_config: DatasetConfig) -> Dataset:
        dataset_id = cls.generate_dataset_id()
        if metadata.owner is None:
            metadata.owner = GflNode.address
        metadata.id = dataset_id
        dataset = Dataset(dataset_id=dataset_id,
                          metadata=metadata,
                          dataset_config=dataset_config)
        lfs.save_dataset(dataset, module)
        return dataset

    @classmethod
    def submit_dataset(cls, dataset_id: str):
        dataset = lfs.load_dataset_zip(dataset_id)
        NetBroadcast.broadcast_dataset(dataset_id, dataset)
