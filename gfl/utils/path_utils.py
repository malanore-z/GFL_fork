import os
from pathlib import PurePath


class PathUtils(object):

    @classmethod
    def join(cls, *paths):
        return PurePath(*paths).as_posix()

    @classmethod
    def user_home_dir(cls):
        return os.path.expanduser("~")

    @classmethod
    def exists(cls, path):
        return os.path.exists(path)
