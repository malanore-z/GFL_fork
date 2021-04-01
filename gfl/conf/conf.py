import yaml

from gfl.utils import PathUtils


class GflConfMetadata(type):

    @property
    def home_dir(cls):
        return cls._GflConf__home_dir

    @home_dir.setter
    def home_dir(cls, value):
        cls._GflConf__home_dir = PathUtils.abspath(value)
        cls._GflConf__data_dir = PathUtils.join(value, "data")
        cls._GflConf__logs_dir = PathUtils.join(value, "logs")
        cls._GflConf__cache_dir = PathUtils.join(value, "cache")

    @property
    def data_dir(cls):
        return cls._GflConf__data_dir

    @property
    def logs_dir(cls):
        return cls._GflConf__logs_dir

    @property
    def cache_dir(cls):
        return cls._GflConf__cache_dir


class GflConf(object, metaclass=GflConfMetadata):
    # 运行时可以修改的参数
    props = {}
    # 从配置文件中读取的参数，运行时不可更改
    readonly_props = {}

    # PathUtils.user_home_dir() /Users/YY
    __home_dir = PathUtils.join(PathUtils.user_home_dir(), ".gfl")  # /Users/YY/.gfl
    __data_dir = PathUtils.join(__home_dir, "data")  # /Users/YY/.gfl/data
    __logs_dir = PathUtils.join(__home_dir, "logs")  # /Users/YY/.gfl/logs
    __cache_dir = PathUtils.join(__home_dir, "cache")  # /Users/YY/.gfl/cache

    """
    读取 /Users/YY/.gfl/conf.yaml 中的配置信息到 readonly_props 中
    """

    @classmethod
    def reload(cls):
        with open(PathUtils.join(cls.__home_dir, "conf.yaml"), "r") as f:  # /Users/YY/.gfl/conf.yaml
            cls.readonly_props = yaml.safe_load(f.read())

    """
    从 readonly_props 中读取 key 对应的信息，如果不存在，则返回 default
    """

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

    """
    将 props 中键为 key 的值设为 value ，如果 key 出现在 readonly_props，则保存
    """

    @classmethod
    def set_property(cls, key, value):
        k_seq = cls.__split_key(key)
        if cls.__exists_in_dict(cls.readonly_props, k_seq):
            raise ValueError("readonly key[%d] cannot be modified." % key)
        cls.__set_to_dict(cls.props, cls.__split_key(key), value)

    """
    将默认配置信息保存到 /Users/YY/.gfl/conf.yaml 中
    """

    @classmethod
    def init_conf(cls):
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
        "enabled": True,
        "server_number": 1,
        "client_number": 5
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
