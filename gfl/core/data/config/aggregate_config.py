from gfl.core.data.config.config import Config


class AggregateConfig(Config):
    # aggregation round
    round: int = 10
    clients_per_round: int = 2

    def with_round(self, round_):
        self.round = round_
        return self

    def with_clients_per_round(self, clients_per_round):
        self.clients_per_round = clients_per_round
        return self

    def get_round(self):
        return self.round

    def get_clients_per_round(self):
        return self.clients_per_round
