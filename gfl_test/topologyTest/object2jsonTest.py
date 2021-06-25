from gfl.conf.node import GflNode
from gfl.core.lfs.data import load_topology_manager, save_topology_manager


def jsonToObject():
    topology_manager = load_topology_manager("f1404379d87f34bda07aba3c530bd146")
    print(topology_manager.topology)
    save_topology_manager("123", topology_manager)
    topology_manager = load_topology_manager("123")
    print(topology_manager.topology)


if __name__ == "__main__":
    jsonToObject()
