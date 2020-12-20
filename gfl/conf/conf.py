from pathlib import PurePath

import yaml

from gfl.conf.path import GflPath


class GflConf(object):
    class standlone:
        enabled = True

    class http:
        enabled = False
        server_url = "127.0.0.1"
        server_port = 9001
        listen_url = "0.0.0.0"
        listen_port = 9001

    class rpc:
        enabled = False
        server_url = "127.0.0.1"
        server_port = 9002
        listen_url = "0.0.0.0"
        listen_port = 9002

    class eth:
        enabled = False
        url = "127.0.0.1"
        port = 8545

    class ipfs:
        enabled = False
        url = "127.0.0.1"
        port = 5001

    @classmethod
    def reload(cls):
        with open(PurePath(GflPath.gfl_dir, GflPath.conf_filename), "r") as f:
            data = yaml.safe_load(f.read())
        cls.__set_all_props(data)

    @classmethod
    def save(cls):
        data = cls.__get_all_props()
        with open(PurePath(GflPath.gfl_dir, GflPath.conf_filename), "w") as f:
            f.write(yaml.safe_dump(data))

    @classmethod
    def __get_all_props(cls):
        return cls.__get_cls_props(cls)

    @classmethod
    def __get_cls_props(cls, subcls):
        ret = {}
        for k, v in subcls.__dict__.items():
            if k.startswith("_"):
                continue
            if isinstance(v, type):
                ret[cls.__yaml_key(k)] = cls.__get_cls_props(v)
                continue
            if callable(getattr(subcls, k)):
                continue
            ret[cls.__yaml_key(k)] = v
        return ret

    @classmethod
    def __set_all_props(cls, data):
        cls.__set_cls_props(cls, data)

    @classmethod
    def __set_cls_props(cls, subcls, data):
        if data is None or len(data) == 0:
            return
        for k, v in subcls.__dict__.items():
            if k.startswith("_"):
                continue
            if isinstance(v, type):
                cls.__set_cls_props(v, data.get(cls.__yaml_key(k)))
                continue
            if callable(getattr(subcls, k)):
                continue
            setattr(subcls, k, data.get(cls.__yaml_key(k)))

    @classmethod
    def __yaml_key(cls, key):
        return key.replace("_", "-")

    @classmethod
    def __cls_key(cls, key):
        return key.replace("-", "_")
