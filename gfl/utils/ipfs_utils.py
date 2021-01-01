from pathlib import PurePath

import ipfshttpclient

from gfl.conf import GflConf, GflPath


class IpfsUtils(object):

    @classmethod
    def put(cls, file_bytes: bytes):
        client = ipfshttpclient.connect(GflConf.ipfs.addr)
        res = client.add_bytes(file_bytes)
        return res["Hash"]

    @classmethod
    def get(cls, ipfs_hash: str):
        client = ipfshttpclient.connect(GflConf.ipfs.addr)
        client.get(ipfs_hash, target=GflPath.tmp_dir)
        path = PurePath(GflPath.tmp_dir, ipfs_hash)
        with open(path, "rb") as f:
            ret = f.read()
        return ret
