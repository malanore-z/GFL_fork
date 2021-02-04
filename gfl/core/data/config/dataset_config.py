
from gfl.core.data.config.config_object import ConfigObject
from gfl.core.data.config.config import Config


class DatasetConfig(Config):

    dataset: ConfigObject
    val_dataset: ConfigObject = None
    val_rate: float = 0.2

    def with_dataset(self, dataset, **kwargs):
        self.dataset = self._set_config_object(dataset, **kwargs)
        return self

    def with_val_dataset(self, val_dataset, **kwargs):
        self.val_dataset = self._set_config_object(val_dataset, **kwargs)
        return self

    def with_val_rate(self, val_rating):
        self.val_rate = val_rating
        return self

    def get_dataset(self):
        return self._get_config_object(self.dataset, None)

    def get_val_dataset(self):
        return self._get_config_object(self.val_dataset, None)

    def get_val_rate(self):
        return self.val_rate
