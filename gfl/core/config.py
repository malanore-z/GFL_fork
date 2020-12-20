__all__ = [
    "ConfigObject",
    "ConfigParser",
    "Config",
    "TrainConfig",
    "AggregateConfig",
    "DatasetConfig",
    "JobConfig"
]

from enum import Enum

from gfl.core.strategy import *
from gfl.utils.po_utils import PlainObject
from gfl.utils.decorate_utils import NotNull, AllArgsNotNone, AnyArgsNotNone


class ConfigObject(PlainObject):
    name = (str,)
    strategy = (str,)
    args = (dict, str)
    is_instance = (bool,)

    def __init__(self, obj=None, **kwargs):
        super(ConfigObject, self).__init__()
        self.name, self.strategy = self.__get_name(obj)
        self.args = kwargs.copy()
        self.is_instance = type(obj) != type

    def __get_name(self, obj):
        if obj is None:
            return None, None
        else:
            if type(obj) == str:
                return obj, Strategy.USER_DEFINED.value
            if isinstance(obj, Enum):
                return None, obj.value
            return obj.__name__, Strategy.USER_DEFINED.value


class ConfigParser(object):

    def __init__(self, module):
        super(ConfigParser, self).__init__()
        self.module = module

    @AllArgsNotNone
    def parse_model(self, model: ConfigObject):
        return self.parse_object(model)

    @AllArgsNotNone
    def parse_loss(self, loss: ConfigObject):
        return self.__parse(loss)

    @AllArgsNotNone
    def parse_optimizer(self, optimizer: ConfigObject, model):
        return self.__parse(optimizer, model.parameters())

    @AllArgsNotNone
    def parse_lr_scheduler(self, lr_scheduler: ConfigObject, optimizer):
        return self.__parse(lr_scheduler, optimizer)

    @AllArgsNotNone
    def parse_dataset(self, dataset: ConfigObject):
        return self.parse_object(dataset)

    def __parse(self, obj, *args):
        instance = None
        if self.__has_strategy(obj):
            instance = self.__parse_strategy(obj, *args)
        if instance is None:
            instance = self.parse_object(obj, *args)
        return instance

    def __parse_strategy(self, obj: ConfigObject, *args):
        strategy_type = StrategyParser.parse(obj.strategy)
        if strategy_type is not None:
            return self.__get_instance(strategy_type, obj.args, *args)
        return None

    @NotNull(all=[1])
    def parse(self, obj: ConfigObject, *args):
        instance = None
        if self.__has_strategy(obj):
            instance = self.parse_strategy(obj, None, *args)
        if instance is None:
            instance = self.parse_object(obj, *args)
        return instance

    @NotNull(all=[1])
    def parse_strategy(self, obj: ConfigObject, strategy_type, *args):
        builtin_type = StrategyParser.parse(obj.strategy, strategy_type)
        if builtin_type is not None:
            return self.__get_instance(builtin_type, obj.args, *args)
        return None

    @NotNull(all=[1])
    def parse_object(self, obj: ConfigObject, *args):
        instance = getattr(self.module, obj.name, None)
        if instance is None:
            return None
        if obj.is_instance:
            return instance
        return self.__get_instance(instance, obj.args, *args)

    def __get_instance(self, instance_type, kwargs, *args):
        if isinstance(kwargs, dict):
            return instance_type(*args, **kwargs)
        return instance_type(*args)

    def __has_strategy(self, obj: ConfigObject):
        if obj.strategy is None or obj.strategy == "":
            return False
        if obj.strategy == Strategy.USER_DEFINED.value or obj.strategy == Strategy.NONE.value:
            return False
        return True


class Config(PlainObject):
    args = (dict, str)

    def with_args(self, **kwargs):
        self.args = kwargs.copy()
        return self


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


class AggregateConfig(Config):
    aggregator = (ConfigObject,)
    epoch = (int,)

    def with_epoch(self, epoch):
        self.epoch = epoch
        return self

    def with_aggregator(self, aggregator, **kwargs):
        self.aggregator = ConfigObject(aggregator, **kwargs)
        return self


class DatasetConfig(Config):
    id = (str,)
    dataset = (ConfigObject,)
    transforms = (ConfigObject,)
    val_dataset = (ConfigObject,)
    val_rate = (float,)

    def with_id(self, id):
        self.id = id
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


class JobConfig(Config):
    owner = (str,)
    round = (int, )
    create_time = (int,)

    def with_owner(self, owner):
        self.owner = owner
        return self

    def with_round(self, round):
        self.round = round
        return self

    def with_create_time(self, create_time):
        self.create_time = create_time
        return self


if __name__ == "__main__":
    train_config = TrainConfig()
