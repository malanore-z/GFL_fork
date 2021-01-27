
from gfl.core.config.config_object import ConfigObject
from gfl.core.config.config import Config, RuntimeConfig


class DatasetConfig(Config):
    dataset_id = (str,)
    dataset = (ConfigObject,)
    transforms = (ConfigObject,)
    val_dataset = (ConfigObject,)
    val_rate = (float,)

    def with_dataset_id(self, id):
        self.dataset_id = id
        return self

    def with_dataset(self, dataset, **kwargs):
        self.dataset = ConfigObject(dataset, **kwargs)
        return self

    def with_transforms(self, transforms, **kwargs):
        self.transforms = ConfigObject(transforms, **kwargs)
        return self

    def with_val_dataset(self, val_dataset, **kwargs):
        self.val_dataset = ConfigObject(val_dataset, **kwargs)
        return self

    def with_val_rate(self, val_rating):
        self.val_rate = val_rating
        return self
