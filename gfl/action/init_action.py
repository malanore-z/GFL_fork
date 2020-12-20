from gfl.conf.initializer import init_gfl
from gfl.conf.path import update_root_dir


def init(args):
    if args.home is not None:
        update_root_dir(args.home)
    init_gfl(args.force)
