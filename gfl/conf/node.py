import json
import os
from pathlib import PurePath

from gfl.conf.path import GflPath


class GflNode(object):
    address = None
    key = None

    @classmethod
    def load_node_key(cls):
        keyfile = PurePath(GflPath.gfl_dir, GflPath.keyjson_filename)
        if not os.path.exists(keyfile):
            raise ValueError("keyfile not exists.")
        with open(keyfile, "r") as f:
            keyjson = json.loads(f.read())
        cls.address = keyjson["address"]
        cls.key = keyjson["key"]
