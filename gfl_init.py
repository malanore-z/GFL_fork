
from gfl.conf import GflConf
from gfl.application import Application
from gfl.shell import Shell


GflConf.home_dir = "data"
GflConf.load()


if __name__ == "__main__":
    Shell.welcome()
    Application.init(True)
