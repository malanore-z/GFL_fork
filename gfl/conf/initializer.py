import json
import os
import shutil
from pathlib import PurePath

from web3 import Web3

from gfl.conf.conf import GflConf
from gfl.conf.node import GflNode
from gfl.conf.path import GflPath


def create_dir():
    os.makedirs(GflPath.gfl_dir, exist_ok=True)
    os.makedirs(GflPath.logs_dir, exist_ok=True)
    os.makedirs(GflPath.data_dir, exist_ok=True)
    os.makedirs(GflPath.job_dir, exist_ok=True)
    os.makedirs(GflPath.client_dir, exist_ok=True)
    os.makedirs(GflPath.server_dir, exist_ok=True)
    os.makedirs(GflPath.dataset_dir, exist_ok=True)


def init_node():
    w3 = Web3()
    account = w3.eth.account.create()
    key_json = {
        "address": account.address[2:],
        "key": account.key.hex()[2:]
    }
    key_json_path = PurePath(GflPath.gfl_dir, GflPath.keyjson_filename).as_posix()
    with open(key_json_path, "w") as f:
        f.write(json.dumps(key_json, indent=4))


def init_conf():
    GflConf.save()


def init_gfl(force=False):
    if os.path.exists(GflPath.gfl_dir):
        if not force:
            print("if you want overwrite old data, use -F arg")
            exit(1)
        else:
            shutil.rmtree(GflPath.gfl_dir)

    create_dir()
    init_node()
    init_conf()


def init_env():
    GflNode.load_node_key()
