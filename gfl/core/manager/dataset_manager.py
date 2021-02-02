
import gfl.core.lfs as lfs
from gfl.core.data.config import DatasetConfig
from gfl.core.manager.manager import Manager


class DatasetManager(Manager):

    @classmethod
    def generate_dataset(cls, module,
                         dataset_config: DatasetConfig) -> DatasetConfig:
        dataset_id = cls.generate_dataset_id()
        dataset_config.with_dataset_id(dataset_id)
        lfs.save_dataset(dataset_config, module)
        return dataset_config

    @classmethod
    def load_dataset(cls, dataset_id):
        return lfs.load_dataset(dataset_id)