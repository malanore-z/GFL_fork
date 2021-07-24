__all__ = [
    "NetBroadcast",
    "NetFetch",
    "NetReceive",
    "NetSend"
]

import warnings

from gfl.conf import GflConf


net_mode = GflConf.get_property("net.mode")

if net_mode == "standalone":
    from gfl.net.standalone import NetBroadcast, NetFetch, NetReceive, NetSend
elif net_mode == "http":
    from gfl.net.http import NetBroadcast, NetFetch, NetReceive, NetSend
elif net_mode == "eth":
    from gfl.net.eth import NetBroadcast, NetFetch, NetReceive, NetSend
elif net_mode is None:
    from gfl.net.abstract import NetBroadcast, NetFetch, NetReceive, NetSend
    warnings.warn("net mode has not set.")
else:
    raise ValueError("unknown net mode.")
