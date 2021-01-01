import json
import os
import shutil
from pathlib import PurePath

from web3 import Web3

from gfl.conf.conf import GflConf
from gfl.conf.path import GflPath


def create_dir():
    dirs = [
        GflPath.gfl_dir,
        GflPath.tmp_dir,
        GflPath.logs_dir,
        GflPath.work_dir, GflPath.server_work_dir, GflPath.client_work_dir,
        GflPath.data_dir, GflPath.job_dir, GflPath.client_dir, GflPath.server_dir, GflPath.dataset_dir
    ]
    for dir in dirs:
        os.makedirs(dir, exist_ok=True)


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
