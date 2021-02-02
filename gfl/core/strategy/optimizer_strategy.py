from enum import Enum

import torch.optim as optim

from gfl.core.strategy.strategy_adapter import StrategyAdapter


class OptimizerStrategy(Enum, StrategyAdapter):

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

    def _torch_type(self):
        return getattr(optim, self.value)
