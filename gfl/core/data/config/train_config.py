
from gfl.core.data.config.config_object import ConfigObject
from gfl.core.data.config.config import Config
from gfl.core.strategy import *


class TrainConfig(Config):
    epoch: int = 10
    batch_size: int = 32
    model: ConfigObject
    optimizer: ConfigObject
    lr_scheduler: ConfigObject
    loss: ConfigObject

    def with_epoch(self, epoch=10):
        self.epoch = epoch
        return self

    def with_batch_size(self, batch_size=32):
        self.batch_size = batch_size
        return self

    def with_model(self, model, **kwargs):
        self.model = self._set_config_object(model, **kwargs)
        return self

    def with_optimizer(self, optimizer, **kwargs):
        self.optimizer = self._set_config_object(optimizer, **kwargs)
        return self

    def with_lr_scheduler(self, scheduler, **kwargs):
        self.lr_scheduler = self._set_config_object(scheduler, **kwargs)
        return self

    def with_loss(self, loss, **kwargs):
        self.loss = self._set_config_object(loss, **kwargs)
        return self

    def get_epoch(self):
        return self.epoch

    def get_batch_size(self):
        return self.batch_size

    def get_model(self):
        return self._get_config_object(self.model, None)

    def get_optimizer(self, model):
        return self._get_config_object(self.optimizer, OptimizerStrategy, model.parameters())

    def get_lr_scheduler(self, optimizer):
        return self._get_config_object(self.lr_scheduler, LRSchedulerStrategy, optimizer)

    def get_loss(self):
        return self._get_config_object(self.loss, LossStrategy)
