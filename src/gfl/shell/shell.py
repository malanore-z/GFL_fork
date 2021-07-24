import os
import sys


class Shell(object):

    @classmethod
    def welcome(cls, **kwargs):
        print("------- GFL -------")
        print("%-20s:%s" % ("pid", str(os.getpid())))

    @classmethod
    def attach(cls, **kwargs):
        pass

    @classmethod
    def startup(cls, **kwargs):
        if sys.stdin is None:
            raise ValueError("F**k")
        while True:
            cmd = input()
            if "EXIT".lower() == cmd.lower():
                break
            print(cmd)

    @classmethod
    def exit(cls, **kwargs):
        pass
