from enum import Enum

import gfl.core.aggregator as aggregator

from gfl.core.strategy.strategy_adapter import StrategyAdapter


class AggregatorStrategy(Enum, StrategyAdapter):

    FED_AVG = "FedAvgAggregator"

    def _torch_type(self):
        return getattr(aggregator, self.value)
