import logging
import os
import shutil
import threading

from daemoniker import Daemonizer

from gfl.api.listener import HttpListener
from gfl.conf import GflConf
from gfl.core.lfs import Lfs
from gfl.core.manager.node import GflNode
from gfl.core.manager.manager import NodeManager
from gfl.shell import Shell
from gfl.utils import PathUtils


class Application(object):

    logger = None
    node_manager = None
    standalone_managers = []

    def __init__(self):
        super(Application, self).__init__()

    @classmethod
    def init(cls, force):
        if os.path.exists(GflConf.home_dir):
            if force:
                logging.shutdown()
                shutil.rmtree(GflConf.home_dir)
            else:
                raise ValueError("homedir not empty.")
        # create home dir
        os.makedirs(GflConf.home_dir)

        # generate config file
        GflConf.generate_config(PathUtils.join(GflConf.home_dir, "config.yaml"))
        # generate node address and key
        GflNode.init_node()
        # create data directories
        Lfs.init()

    @classmethod
    def run(cls, role, console, **kwargs):
        cls.logger = logging.getLogger("gfl")
        with Daemonizer() as (is_setup, daemonizer):
            main_pid = None
            if is_setup:
                main_pid = os.getpid()
            pid_file = PathUtils.join(GflConf.home_dir, "proc.lock")
            stdout_file = PathUtils.join(GflConf.logs_dir, "console_out")
            stderr_file = PathUtils.join(GflConf.logs_dir, "console_err")
            is_parent = daemonizer(pid_file, stdout_goto=stdout_file, stderr_goto=stderr_file)
            if is_parent:
                if console and main_pid == os.getpid():
                    Shell.startup()

        GflNode.load_node()

        if GflConf.get_property("net.mode") == "standalone":
            client_number = GflConf.get_property("net.standalone.client_number")
            for _ in range(len(GflNode.standalone_nodes), client_number):
                GflNode.add_standalone_node()

            cls.node_manager = NodeManager(node=GflNode.default_node, role="server")

            for i in range(client_number):
                client_manager = NodeManager(node=GflNode.standalone_nodes[i], role="client")
                cls.standalone_managers.append(client_manager)
        else:
            cls.node_manager = NodeManager(node=GflNode.default_node, role=role)

        cls.__startup_node_managers()
        HttpListener.start()

    @classmethod
    def __startup_node_managers(cls):
        # 遍历所有的NodeManager
        threading.Thread(target=cls.node_manager.run).start()
        for nm in cls.standalone_managers:
            t = threading.Thread(target=nm.run)
            t.start()
