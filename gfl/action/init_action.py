import os
import shutil

from gfl.conf import GflConf
from gfl.conf.node import GflNode
from gfl.core.lfs import init_lfs


def init_gfl(force: bool):
    if os.path.exists(GflConf.home_dir):
        if force:
            shutil.rmtree(GflConf.home_dir)
        else:
            raise ValueError("home dir not empty.")
    # 创建节点根目录
    os.makedirs(GflConf.home_dir)
    # 初始化节点地址和密钥对
    GflNode.init_node()
    # 创建默认配置文件
    GflConf.init_conf()
    # 初始化节点数据目录
    init_lfs()


def init(args):
    if args.home is not None:
        GflConf.home_dir = args.home
    init_gfl(args.force)
