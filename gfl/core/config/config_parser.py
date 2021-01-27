
from gfl.core.config.config_object import ConfigObject
from gfl.core.strategy import Strategy, StrategyParser
from gfl.utils.decorate_utils import NotNull, AllArgsNotNone


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