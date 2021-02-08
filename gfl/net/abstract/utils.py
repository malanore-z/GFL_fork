__all__ = [
    "get_property",
    "set_property"
]

from gfl.conf import GflConf


def get_property(key, default=None):
    return GflConf.get_property(key, default)


def set_property(key, value):
    GflConf.set_property(key, value)
