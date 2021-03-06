
from gfl.application import Application
from gfl.conf import GflConf


def server(args):
    if args.home is not None:
        GflConf.home_dir = args.home
    Application.run(role="server", daemon=args.d)
