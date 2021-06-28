from gfl.core.data.config.config import Config
from gfl.core.data.config.config_object import ConfigObject
from gfl.core.strategy import *


class AggregateConfig(Config):
    # aggregation round
    round: int = 10
    clients_per_round: int = 2
    do_validation: bool = False
    batch_size: int = 32
    loss: ConfigObject

    def with_round(self, round_):
        self.round = round_
        return self

    def with_clients_per_round(self, clients_per_round):
        self.clients_per_round = clients_per_round
        return self

    def with_batch_size(self, batch_size=32):
        self.batch_size = batch_size
        return self

    def with_loss(self, loss, **kwargs):
        self.loss = self._set_config_object(loss, **kwargs)
        return self

    def get_round(self):
        return self.round

    def get_batch_size(self):
        return self.batch_size

    def get_loss(self):
        return self._get_config_object(self.loss, LossStrategy)