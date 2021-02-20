import sys
import threading

from daemoniker import Daemonizer

from gfl.conf import GflConf
from gfl.conf.node import GflNode
from gfl.node.manager import NodeManager
from gfl.utils import PathUtils


class Application(object):

    node_managers = []

    def __init__(self):
        super(Application, self).__init__()

    @classmethod
    def run(cls, **kwargs):
        daemon = kwargs.pop("daemon", False)
        if daemon:
            print("DAEMON")
            with Daemonizer() as (is_setup, daemonizer):
                if is_setup:
                    pass
                pid_file = "proc.lock"
                stdout_file = PathUtils.join(GflConf.logs_dir, "console_out")
                stderr_file = PathUtils.join(GflConf.logs_dir, "console_err")
                is_parent = daemonizer(pid_file, stdout_goto=stdout_file, stderr_goto=stderr_file)
                if is_parent:
                    pass

        GflConf.reload()
        GflNode.load_node()

        if GflConf.get_property("standalone.enabled"):
            server_number = GflConf.get_property("standalone.server_number")
            client_number = GflConf.get_property("standalone.client_number")
            for _ in range(len(GflNode.standalone_nodes), server_number + client_number):
                GflNode.add_standalone_node()
            for i in range(0, server_number):
                node_manager = NodeManager(node=GflNode.standalone_nodes[i], role="server")
                cls.node_managers.append(node_manager)
            for i in range(server_number, server_number + client_number):
                node_manager = NodeManager(node=GflNode.standalone_nodes[i], role="client")
                cls.node_managers.append(node_manager)
        else:
            role = kwargs.pop("role")
            print(role)
            node_manager = NodeManager(node=GflNode.default_node, role=role)
            cls.node_managers.append(node_manager)
        cls.__startup_node_managers()

    @classmethod
    def __startup_node_managers(cls):
        for nm in cls.node_managers:
            t = threading.Thread(target=nm.run)
            t.start()
