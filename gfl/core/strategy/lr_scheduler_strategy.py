from enum import Enum

import torch.optim.lr_scheduler as lr_scheduler

from gfl.core.strategy.strategy_adapter import StrategyAdapter


class LRSchedulerStrategy(Enum, StrategyAdapter):

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

    def _torch_type(self):
        return getattr(lr_scheduler, self.value)
