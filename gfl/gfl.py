__all__ = [
    "device",
    "home_dir",
    "get_property",
    "set_property"
]

import os
from pathlib import PurePath

import torch

from gfl.conf import GflConf


device = "cuda:0" if torch.cuda.is_available() else "cpu"


home_dir = PurePath(os.path.expanduser("~"), ".gfl").as_posix()


def get_property(key, default=None):
    return GflConf.get_property(key, default)


def set_property(key, value):
    GflConf.set_property(key, value)
