
from gfl.core.config.config_object import ConfigObject
from gfl.core.config.config import Config, RuntimeConfig


class TrainConfig(Config):
    epoch = (int,)
    batch_size = (int,)
    model = (ConfigObject,)
    optimizer = (ConfigObject,)
    lr_scheduler = (ConfigObject,)
    loss = (ConfigObject,)

    def with_epoch(self, epoch=10):
        self.epoch = epoch
        return self

    def with_batch_size(self, batch_size=32):
        self.batch_size = batch_size
        return self

    def with_model(self, model, **kwargs):
        self.model = ConfigObject(model, **kwargs)
        return self

    def with_optimizer(self, optimizer, **kwargs):
        self.optimizer = ConfigObject(optimizer, **kwargs)
        return self

    def with_lr_scheduler(self, scheduler, **kwargs):
        self.lr_scheduler = ConfigObject(scheduler, **kwargs)
        return self

    def with_loss(self, loss, **kwargs):
        self.loss = ConfigObject(loss, **kwargs)
        return self


class TrainRuntimeConfig(RuntimeConfig):

    def __init__(self, *args, **kwargs):
        super(TrainRuntimeConfig, self).__init__(*args, **kwargs)
        self.epoch = kwargs.pop("epoch")
        self.batch_size = kwargs.pop("batch_size")
