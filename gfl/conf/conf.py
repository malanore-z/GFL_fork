from pathlib import PurePath

import yaml

from gfl.conf.path import GflPath


class GflConf(object):

    props = {}
    readonly_props = {}

    @classmethod
    def reload(cls):
        with open(PurePath(GflPath.gfl_dir, GflPath.conf_filename), "r") as f:
            cls.readonly_props = yaml.safe_load(f.read())

    @classmethod
    def get_property(cls, key, default=None):
        op_res, readonly_val = cls.__get_from_dict(cls.readonly_props,
                                                   cls.__split_key(key),
                                                   default)
        if op_res:
            return readonly_val
        return cls.__get_from_dict(cls.readonly_props,
                                   cls.__split_key(key),
                                   default)[1]

    @classmethod
    def set_property(cls, key, value):
        k_seq = cls.__split_key(key)
        if cls.__exists_in_dict(cls.readonly_props, k_seq):
            raise ValueError("readonly key[%d] cannot be modified." % key)
        cls.__set_to_dict(cls.props, cls.__split_key(key), value)

    @classmethod
    def __split_key(cls, key: str):
        if key is None or key.strip() == "":
            raise ValueError("key cannot be none or empty.")
        return key.split(".")

    @classmethod
    def __exists_in_dict(cls, d: dict, k_seq: list):
        if k_seq is None or len(k_seq) == 0:
            return False
        for k in k_seq:
            if k in d:
                d = d[k]
            else:
                return False
        return True

    @classmethod
    def __get_from_dict(cls, d: dict, k_seq: list, default=None):
        if k_seq is None or len(k_seq) == 0:
            raise ValueError("key cannot be none or empty")
        for k in k_seq:
            if k in d:
                d = d[k]
            else:
                return False, default
        return True, d

    @classmethod
    def __set_to_dict(cls, d: dict, k_seq: list, value):
        if k_seq is None or len(k_seq) == 0:
            raise ValueError("key cannot be none or empty")
        for k in k_seq[:-1]:
            if k not in d:
                d[k] = {}
            d = d[k]

        d[k_seq[-1]] = value
