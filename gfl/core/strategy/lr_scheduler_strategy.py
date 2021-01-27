from enum import Enum

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
