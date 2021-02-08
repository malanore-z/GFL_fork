__all__ = [
    "NetBroadcast",
    "NetFetch",
    "NetReceive",
    "NetSend"
]

from gfl.net.standlone.broadcast import StandaloneBroadcast as NetBroadcast
from gfl.net.standlone.fetch import StandaloneFetch as NetFetch
from gfl.net.standlone.receive import StandaloneReceive as NetReceive
from gfl.net.standlone.send import StandaloneSend as NetSend