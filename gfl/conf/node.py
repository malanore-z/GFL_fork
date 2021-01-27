import json
import os

from web3 import Web3

import gfl
from gfl.utils import PathUtils


class GflNode(object):

    key_filename = "key.json"
    address = None
    key = None

    @classmethod
    def init_node(cls):
        gfl_dir = gfl.home_dir

        keyfile = PathUtils.join(gfl_dir, cls.key_filename)
        w3 = Web3()
        account = w3.eth.account.create()
        key_json = {
            "address": account.address[2:],
            "key": account.key.hex()[2:]
        }
        with open(keyfile, "w") as f:
            f.write(json.dumps(key_json, indent=4))

    @classmethod
    def load_node(cls):
        gfl_dir = gfl.home_dir

        keyfile = PathUtils.join(gfl_dir, cls.key_filename)
        if not os.path.exists(keyfile):
            raise ValueError("keyfile not exists.")
        with open(keyfile, "r") as f:
            keyjson = json.loads(f.read())
        cls.address = keyjson["address"]
        cls.key = keyjson["key"]
