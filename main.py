
from gfl.conf import GflConf
from gfl.application import Application
from gfl.shell import Shell


GflConf.home_dir = "data"
GflConf.load()


if __name__ == "__main__":
    console = True
    role = "server"

    Shell.welcome()
    # Application.init(True)
    Application.run(role, console)
