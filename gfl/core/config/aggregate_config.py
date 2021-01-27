
from gfl.core.config.config_object import ConfigObject
from gfl.core.config.config import Config, RuntimeConfig


class AggregateConfig(Config):
    aggregator = (ConfigObject,)
    epoch = (int,)

    def with_epoch(self, epoch):
        self.epoch = epoch
        return self

    def with_aggregator(self, aggregator, **kwargs):
        self.aggregator = ConfigObject(aggregator, **kwargs)
        return self


class AggregateRuntimeConfig(RuntimeConfig):

    def __init__(self, *args, **kwargs):
        super(AggregateRuntimeConfig, self).__init__(*args, **kwargs)
