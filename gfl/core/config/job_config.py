
from gfl.core.config.config_object import ConfigObject
from gfl.core.config.config import Config, RuntimeConfig


class JobConfig(Config):
    owner = (str,)
    round = (int, )
    create_time = (int,)

    def with_owner(self, owner):
        self.owner = owner
        return self

    def with_round(self, round):
        self.round = round
        return self

    def with_create_time(self, create_time):
        self.create_time = create_time
        return self


class JobRuntimeConfig(RuntimeConfig):

    def __init__(self):
        super(JobRuntimeConfig, self).__init__()
