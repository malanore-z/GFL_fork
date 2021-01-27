__all__ = [
    "node_key",
    "node_address",
    "get_property",
    "set_property"
]

from gfl.conf import GflNode, GflConf


def node_key():
    return GflNode.key


def node_address():
    return GflNode.address


def get_property(key, default=None):
    return GflConf.get_property(key, default)


def set_property(key, value):
    GflConf.set_property(key, value)
