from pathlib import PurePath

import ipfshttpclient

from gfl.conf import GflConf
from gfl.core.lfs.path import cache_dir
from gfl.utils.path_utils import PathUtils


ipfs_addr = GflConf.get_property("ipfs.addr")
tmp_dir = GflConf.get_property("dir.tmp")


class Ipfs(object):

    @classmethod
    def put(cls, file_bytes: bytes):
        client = ipfshttpclient.connect(ipfs_addr)
        res = client.add_bytes(file_bytes)
        return res["Hash"]

    @classmethod
    def get(cls, ipfs_hash: str):
        client = ipfshttpclient.connect(ipfs_addr)
        client.get(ipfs_hash, target=cache_dir())
        path = PathUtils.join(cache_dir(), ipfs_hash)
        with open(path, "rb") as f:
            ret = f.read()
        return ret