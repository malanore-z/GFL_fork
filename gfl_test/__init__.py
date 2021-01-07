import os

from gfl.conf.initializer import init_env, init_gfl
from gfl.conf.path import update_root_dir


work_dir = os.path.dirname(os.path.dirname(__file__))
os.chdir(work_dir)

update_root_dir("data")


if not os.path.exists("data"):
    init_gfl()

init_env()
