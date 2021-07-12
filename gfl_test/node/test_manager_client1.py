import gfl_test
from gfl.conf.node import GflNode
from gfl.node.manager import NodeManager

if __name__ == '__main__':
    GflNode.load_node()
    # node_server = GflNode.standalone_nodes[0]
    node_client1 = GflNode.standalone_nodes[1]
    # node_client2 = GflNode.standalone_nodes[2]
    # self.node_manager_server = NodeManager(node=node_server, role="server")
    node_manager_client1 = NodeManager(node=node_client1, role="client")
    node_manager_client1.run()
