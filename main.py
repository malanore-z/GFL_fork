from gfl.application import Application
from gfl.conf import GflConf


if __name__ == "__main__":
    GflConf.home_dir = "data"
    Application.run(daemon=False)
