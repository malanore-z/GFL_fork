
from gfl.conf import GflNode


def blank(**kwargs):
    return kwargs


def add_client(**kwargs):
    kwargs["client"] = GflNode.address
    return kwargs
