import yaml

from gfl.utils import PathUtils


class GflConfMetadata(type):

    @property
    def home_dir(cls):
        return cls._GflConf__home_dir

    @home_dir.setter
    def home_dir(cls, value):
        cls._GflConf__home_dir = value


class GflConf(object, metaclass=GflConfMetadata):

    # Parameters that can be modified at run time
    props = {}
    # Parameters that are read from a configuration file and cannot be changed at run time
    readonly_props = {}
    # home directory
    __home_dir = PathUtils.join(PathUtils.user_home_dir(), ".gfl")


    @classmethod
    def reload(cls):
        """
        Reload readonly parameters from the YAML file.
        :return:
        """
        with open(PathUtils.join(cls.__home_dir, "conf.yaml"), "r") as f:
            cls.readonly_props = yaml.safe_load(f.read())

    @classmethod
    def get_property(cls, key, default=None):
        """
        Get the value of readonly parameters.

        :param key: a string of the key to get the value
        """
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
        """
        Set parameters at run time.
        """
        k_seq = cls.__split_key(key)
        if cls.__exists_in_dict(cls.readonly_props, k_seq):
            raise ValueError("readonly key[%d] cannot be modified." % key)
        cls.__set_to_dict(cls.props, cls.__split_key(key), value)

    @classmethod
    def init_conf(cls):
        """
        Serialize default configuration into a YAML stream.
        """
        with open(PathUtils.join(cls.__home_dir, "conf.yaml"), "w") as f:
            yaml.safe_dump(default_conf, f)

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


default_conf = {
    "standalone": {
        "enabled": True
    },
    "http": {
        "enabled": False,
        "server_url": "127.0.0.1",
        "server_port": 9001,
        "listen_url": "127.0.0.1",
        "listen_port": 9001
    },
    "eth": {
        "enabled": False,
        "url": "127.0.0.1",
        "port": 8545
    },
    "ipfs": {
        "enabled": False,
        "addr": "/dns/localhost/tcp/5001/http"
    }
}

