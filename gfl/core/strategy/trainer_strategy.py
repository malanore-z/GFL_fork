from enum import Enum

from gfl.core.strategy.strategy_adapter import StrategyAdapter


class TrainerStrategy(StrategyAdapter, Enum):

    SUPERVISED = "SupervisedTrainer"

    def _torch_type(self):
        import gfl.core.trainer as trainer
        return getattr(trainer, self.value)
