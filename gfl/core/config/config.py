from gfl.core.config.config_object import ConfigObject
from gfl.utils.po_utils import PlainObject


class Config(PlainObject):
    args = (dict, str)

    def with_args(self, **kwargs):
        self.args = kwargs.copy()
        return self


class RuntimeConfig(object):

    def __init__(self, *args, **kwargs):
        super(RuntimeConfig, self).__init__(*args, **kwargs)
        self.args = kwargs.pop("args", {})
