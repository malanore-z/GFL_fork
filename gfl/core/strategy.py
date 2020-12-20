__all__ = [
    "Strategy",
    "AggregateStrategy",
    "LossStrategy",
    "OptimizerStrategy",
    "LRSchedulerStrategy",
    "StrategyParser"
]

from enum import Enum
from typing import Union

import torch.nn as nn
import torch.optim as optim
import torch.optim.lr_scheduler as lr_scheduler


class Strategy(Enum):
    USER_DEFINED = "user_defined"
    NONE = "none"


class AggregateStrategy(Enum):
    FED_AVG = "fed_avg"
    FED_DISTILLATION = "fed_distillation"


class LossStrategy(Enum):
    L1 = "L1Loss"
    NLL = "NLLLoss"
    POISSON_NLL = "PoissonNLLLoss"
    KL_DIV = "KLDivLoss"
    MSE = "MSELoss"
    BCE = "BCELoss"
    BCE_WITH_LOGITS = "BCEWithLogitsLoss"
    HINGE_EMBEDDING = "HingeEmbeddingLoss"
    MULTI_LABEL_MARGIN = "MultiLabelMarginLoss"
    SMOOTH_L1 = "SmoothL1Loss"
    SOFT_MARGIN = "SoftMarginLoss"
    CROSS_ENTROPY = "CrossEntropyLoss"
    MULTI_LABEL_SOFT_MARGIN = "MultiLabelSoftMarginLoss"
    COSINE_EMBEDDING = "CosineEmbeddingLoss"
    MARGIN_RANKING = "MarginRankingLoss"
    MULTI_MARGIN = "MultiMarginLoss"
    TRIPLE_MARGIN = "TripletMarginLoss"
    CTC = "CTCLoss"


class OptimizerStrategy(Enum):
    SGD = "SGD"
    ASGD = "ASGD"
    RPROP = "Rprop"
    ADAGRAD = "Adagrad"
    ADADELTA = "Adadelta"
    RMSprop = "RMSprop"
    ADAM = "Adam"
    ADAMW = "AdamW"
    ADAMAX = "Adamax"
    SPARSE_ADAM = "SparseAdam"
    LBFGS = "LBFGS"


class LRSchedulerStrategy(Enum):
    LAMBDA_LR = "LambdaLR"
    MULTIPLICATIVE_LR = "MultiplicativeLR"
    STEP_LR = "StepLR"
    MULTI_STEP_LR = "MultiStepLR"
    EXPONENTIAL_LR = "ExponentialLR"
    COSINE_ANNEALING_LR = "CosineAnnealingLR"
    ReduceLROnPlateau = "ReduceLROnPlateau"
    CYCLIC_LR = "CyclicLR"
    COSINE_ANNEALING_WARM_RESTARTS = "CosineAnnealingWarmRestarts"
    ONE_CYCLE_LR = "OneCycleLR"


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
