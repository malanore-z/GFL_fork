from gfl.core.manager.node import GflNode
from gfl.core.manager.manager import NodeManager

if __name__ == '__main__':
    GflNode.load_node()
    # node_server = GflNode.standalone_nodes[0]
    # node_client1 = GflNode.standalone_nodes[1]
    node_client2 = GflNode.standalone_nodes[2]
    # self.node_manager_server = NodeManager(manager=node_server, role="server")
    node_manager_client2 = NodeManager(node=node_client2, role="client")
    node_manager_client2.run()
