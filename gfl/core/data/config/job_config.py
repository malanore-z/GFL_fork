
from gfl.core.data.config.config_object import ConfigObject
from gfl.core.data.config.config import Config
from gfl.core.strategy import *


class JobConfig(Config):

    trainer: ConfigObject
    aggregator: ConfigObject

    def with_trainer(self, trainer, **kwargs):
        self.trainer = self._set_config_object(trainer, **kwargs)
        return self

    def with_aggregator(self, aggregator, **kwargs):
        self.aggregator = self._set_config_object(aggregator, **kwargs)
        return self

    def get_trainer(self):
        return self._get_config_object(self.trainer, TrainerStrategy)

    def get_aggregator(self):
        return self._get_config_object(self.aggregator, AggregatorStrategy)
