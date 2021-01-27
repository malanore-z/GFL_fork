from typing import Union

import torch.nn as nn
import torch.optim as optim
import torch.optim.lr_scheduler as lr_scheduler

from gfl.core.strategy.aggregate_strategy import AggregateStrategy
from gfl.core.strategy.loss_strategy import LossStrategy
from gfl.core.strategy.lr_scheduler_strategy import LRSchedulerStrategy
from gfl.core.strategy.optimizer_strategy import OptimizerStrategy


class StrategyParser(object):

    @classmethod
    def parse(cls, strategy: Union[str, LossStrategy, OptimizerStrategy, LRSchedulerStrategy], strategy_type=None):
        if strategy_type is None:
            strategy_type = cls.__parse_type(strategy)
        if strategy_type == LossStrategy:
            return cls.parse_loss(strategy)
        if strategy_type == OptimizerStrategy:
            return cls.parse_optimizer(strategy)
        if strategy_type == LRSchedulerStrategy:
            return cls.parse_lr_scheduler(strategy)

    @classmethod
    def parse_loss(cls, strategy: Union[str, LossStrategy]):
        return cls.__parse_strategy(strategy, LossStrategy, nn)

    @classmethod
    def parse_optimizer(cls, strategy: Union[str, OptimizerStrategy]):
        return cls.__parse_strategy(strategy, OptimizerStrategy, optim)

    @classmethod
    def parse_lr_scheduler(cls, strategy: Union[str, LRSchedulerStrategy]):
        return cls.__parse_strategy(strategy, LRSchedulerStrategy, lr_scheduler)

    @classmethod
    def __parse_strategy(cls, strategy, strategy_type, module):
        if strategy is None:
            return None
        if type(strategy) is str:
            try:
                strategy = strategy_type(strategy)
            except:
                return None
        return getattr(module, strategy.value)

    @classmethod
    def __parse_type(cls, strategy):
        if isinstance(strategy, LossStrategy):
            return LossStrategy
        if isinstance(strategy, OptimizerStrategy):
            return OptimizerStrategy
        if isinstance(strategy, LRSchedulerStrategy):
            return LRSchedulerStrategy
        if isinstance(strategy, str):
            if cls.__is_enum_instance(strategy, LossStrategy):
                return LossStrategy
            if cls.__is_enum_instance(strategy, OptimizerStrategy):
                return OptimizerStrategy
            if cls.__is_enum_instance(strategy, LRSchedulerStrategy):
                return LRSchedulerStrategy
        raise TypeError("Unknown strategy type[%s]." % strategy)

    @classmethod
    def __is_enum_instance(cls, instance: str, enum_type):
        for k, v in enum_type.__members__.items():
            if v.value == instance:
                return True
        return False