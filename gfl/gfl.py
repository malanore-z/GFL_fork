__all__ = [
    "device"
]

import torch


class Properties(object):

    device = "cuda:0" if torch.cuda.is_available() else "cpu"


def device(val=None):
    if val is not None:
        Properties.device = val
    else:
        return Properties.device
