import os

from gfl.conf.path import update_root_dir


work_dir = os.path.dirname(os.path.dirname(__file__))
os.chdir(work_dir)

update_root_dir("data")
