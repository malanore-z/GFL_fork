
import os


work_dir = os.path.dirname(os.path.dirname(__file__))
os.chdir(work_dir)


from gfl.conf import GflConf
from gfl.conf.node import GflNode
GflConf.home_dir = "data"
GflNode.load_node()
