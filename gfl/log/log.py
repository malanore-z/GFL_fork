import threading
import time

from gfl.conf import GflConf
from gfl.utils import PathUtils


class LogBase(object):

    _instances = {}
    _lock = threading.Lock()

    def __init__(self, name):
        super(LogBase, self).__init__()
        self.__name = name
        self.__last_access_time = time.time()

    def __new__(cls, name):
        if name is None:
            return object.__new__(cls)
        cls._lock.acquire()
        if len(cls._instances) > 127:
            cls._clear()
        obj = cls._instances.get(name)
        if obj is None:
            obj = object.__new__(cls)
            cls._instances[name] = obj
        cls._lock.release()
        return obj

    @classmethod
    def _clear(cls):
        pop_id = ""
        earliest_time = time.time()
        for k, v in cls._instances.items():
            if v.__last_access_time < earliest_time:
                earliest_time = v.__last_access_time
                pop_id = v.__id
        cls._instances.pop(pop_id)

    @property
    def name(self):
        return self.__name


class Log(LogBase):

    debug_filename = PathUtils.join(GflConf.logs_dir, "debug.log")
    info_filename = PathUtils.join(GflConf.logs_dir, "info.log")
    warn_filename = PathUtils.join(GflConf.logs_dir, "warn.log")
    error_filename = PathUtils.join(GflConf.logs_dir, "error.log")

    def __init__(self, name):
        super(Log, self).__init__(name)

    def debug(self, msg, *params):
        pass

    def info(self, msg, *params):
        pass

    def warn(self, msg, *params):
        pass

    def error(self, msg, *params):
        pass
