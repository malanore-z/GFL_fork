from gfl.core.manager.node import GflNode
from gfl.core.lfs.lfs import load_topology_manager, save_topology_manager


def jsonToObject():
    topology_manager = load_topology_manager("f1404379d87f34bda07aba3c530bd146")
    GflNode.init_node()
    node = GflNode.default_node
    topology_manager.add_client(client_node=node, add_into_topology=True)
    print(topology_manager.get_index_by_node(node))
    topology_manager.generate_topology()
    save_topology_manager("123", topology_manager)
    temp_topology_manager = load_topology_manager("123")
    print(temp_topology_manager.topology)


if __name__ == "__main__":
    jsonToObject()
