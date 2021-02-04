from enum import Enum

from gfl.core.strategy.strategy_adapter import StrategyAdapter


class AggregatorStrategy(StrategyAdapter, Enum):

    FED_AVG = "FedAvgAggregator"

    def _torch_type(self):
        import gfl.core.aggregator as aggregator
        return getattr(aggregator, self.value)
