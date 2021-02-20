from gfl.core.data.config.config import Config


class AggregateConfig(Config):
    # aggregation round
    round: int = 10

    def with_round(self, round_):
        self.round = round_
        return self

    def get_round(self):
        return self.round