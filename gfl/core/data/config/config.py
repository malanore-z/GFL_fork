from enum import Enum
from typing import Dict, Any

from gfl.core.data.config.config_object import ConfigObject
from gfl.core.strategy import *
from gfl.utils.po_utils import PlainObject


class Config(PlainObject):

    args: Dict[str, Any] = {}

    def __init__(self, *, module=None, **kwargs):
        super(Config, self).__init__(**kwargs)
        self.module = module

    def with_args(self, **kwargs):
        self.args = kwargs.copy()
        return self

    def _set_config_object(self, obj, **kwargs):
        if isinstance(obj, Enum):
            return ConfigObject.new_object(strategy=obj, **kwargs)
        else:
            return ConfigObject.new_object(module=self.module, obj=obj, **kwargs)

    def _get_config_object(self, obj: ConfigObject, strategy_type, *args, **kwargs):
        if obj.is_instance:
            if obj.is_builtin:
                strategy: StrategyAdapter = strategy_type(obj.name)
                return strategy.get_type()
            else:
                if self.module is None:
                    raise ValueError("")
                return getattr(self.module, obj.name)
        else:
            if obj.is_builtin:
                strategy: StrategyAdapter = strategy_type(obj.name)
                clazz = strategy.get_type()
            else:
                if self.module is None:
                    raise ValueError("")
                clazz = getattr(self.module, obj.name)
            kwargs_copy = kwargs.copy()
            for k, v in obj.args.items():
                kwargs_copy[k] = v
            return clazz(*args, **kwargs_copy)
