import sys
import threading
import logging

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
        # 加载配置文件
        logging.config.fileConfig('/Users/YY/PycharmProjects/GFL_fork/gfl/log/Logging.conf')
        # 创建 logger
        logger = logging.getLogger('root')
        # 判断是否作为守护进程启用
        # GFL中的进程一般都是作为守护进程来使用
        # 守护进程就是指那些在后台运行的进程
        daemon = kwargs.pop("daemon", False)
        if daemon:
            print("DAEMON")
            logger.info("this is DAEMON")
            with Daemonizer() as (is_setup, daemonizer):
                if is_setup:
                    pass
                # pid是进程的标识符
                pid_file = "proc.lock"
                # stdout_file表示输出日志文件的绝对路径, 收集启动过程中的错误日志
                stdout_file = PathUtils.join(GflConf.logs_dir, "console_out")
                # stderr_file表示错误日志文件的绝对路径, 收集启动过程中的错误日志
                stderr_file = PathUtils.join(GflConf.logs_dir, "console_err")
                is_parent = daemonizer(pid_file, stdout_goto=stdout_file, stderr_goto=stderr_file)
                if is_parent:
                    pass

        # 加载配置
        GflConf.reload()
        # 加载GFL结点
        GflNode.load_node()

        # get_property: Get the value of readonly parameters.
        # 得到standalone.enabled参数，standalone：单机
        if GflConf.get_property("standalone.enabled"):
            server_number = GflConf.get_property("standalone.server_number")
            client_number = GflConf.get_property("standalone.client_number")
            logger.info("the number of server : %s", server_number)
            logger.info("the number of client : %s", client_number)
            for _ in range(len(GflNode.standalone_nodes), server_number + client_number):
                GflNode.add_standalone_node()
            for i in range(0, server_number):
                node_manager = NodeManager(node=GflNode.standalone_nodes[i], role="server")
                cls.node_managers.append(node_manager)
            for i in range(server_number, server_number + client_number):
                node_manager = NodeManager(node=GflNode.standalone_nodes[i], role="client")
                cls.node_managers.append(node_manager)
        else:
            # 得到role参数
            role = kwargs.pop("role")
            print(role)
            logger.info("the role is : %s", role)
            node_manager = NodeManager(node=GflNode.default_node, role=role)
            cls.node_managers.append(node_manager)
        logger.info("GFL is ready.Starting up node managers.")
        cls.__startup_node_managers()

    @classmethod
    def __startup_node_managers(cls):
        # 遍历所有的NodeManager
        for nm in cls.node_managers:
            t = threading.Thread(target=nm.run)
            t.start()
