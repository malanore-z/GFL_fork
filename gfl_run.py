import sys

from gfl.conf import GflConf
from gfl.application import Application
from gfl.shell import Shell


GflConf.home_dir = "data"
GflConf.load()


if __name__ == "__main__":
    sys.stderr = open("std.err", "w")
    console = True
    role = "server"

    Shell.welcome()
    Application.run(role, console)
    sys.stderr.close()
