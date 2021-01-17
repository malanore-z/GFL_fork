__all__ = [
    "device"
]

import torch


device = "cuda:0" if torch.cuda.is_available() else "cpu"


def get_property(key, default=None):
    pass


def set_property(key, value):
    pass
