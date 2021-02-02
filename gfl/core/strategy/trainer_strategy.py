from enum import Enum

import gfl.core.trainer as trainer
from gfl.core.strategy.strategy_adapter import StrategyAdapter


class TrainerStrategy(Enum, StrategyAdapter):

    SUPERVISED = "SupervisedTrainer"

    def _torch_type(self):
        return getattr(trainer, self.value)
