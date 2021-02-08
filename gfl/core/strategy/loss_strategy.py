from enum import Enum

import torch.nn as nn

from gfl.core.strategy.strategy_adapter import StrategyAdapter


class LossStrategy(StrategyAdapter, Enum):

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

    def _torch_type(self):
        return getattr(nn, self.value)