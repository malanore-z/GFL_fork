import argparse

import gfl.action as gfl_action


parser = argparse.ArgumentParser(prog="GFL")
subparsers = parser.add_subparsers(dest="action", title="actions")

init_parser = subparsers.add_parser("init", help="init gfl env")
init_parser.add_argument("--home", type=str)
init_parser.add_argument("-F", "--force", action="store_true")

server_parser = subparsers.add_parser("server", help="startup gfl server")
server_parser.add_argument("--home", type=str)
server_parser.add_argument("-d", action="store_true")
server_parser.add_argument("-D", dest="props", action="append", type=str)

client_parser = subparsers.add_parser("client", help="startup gfl client")
client_parser.add_argument("--home", type=str)
client_parser.add_argument("-d", action="store_true")

attach_parser = subparsers.add_parser("attach", help="connect to gfl net")
attach_parser.add_argument("--host", type=str, default="127.0.0.1")
attach_parser.add_argument("--port", type=int, default=7878)


if __name__ == "__main__":
    args = parser.parse_args()
    if args.action == "init":
        gfl_action.init(args)
    elif args.action == "server":
        gfl_action.server(args)
    elif args.action == "client":
        gfl_action.client(args)
    elif args.action == "attach":
        gfl_action.attach(args)
    else:
        print("unknown action.")
