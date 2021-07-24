from gfl.core.manager.node import GflNode
from gfl.core.lfs.lfs import save_topology_manager
from gfl.core import TopologyConfig
from gfl.core import JobManager, DatasetManager
from gfl.core.generator import DatasetGenerator, JobGenerator

import tests.gfl_test.model as fl_model
from tests import gfl_test as fl_dataset
from gfl.topology import CentralizedTopologyManager


def generate_dataset():
    generator = DatasetGenerator(fl_dataset)
    generator.metadata.content = "mnist dataset"
    generator.dataset_config.with_dataset(fl_dataset.mnist_dataset)
    generator.dataset_config.with_val_rate(0.2)
    dataset = generator.generate()
    DatasetManager.submit_dataset(dataset)
    print(dataset.dataset_id)
    return dataset


def generate_job():
    generator = JobGenerator(fl_model)
    generator.metadata.content = "mnist CNN"
    generator.job_config.with_trainer(TrainerStrategy.SUPERVISED)
    # generator.job_config.with_trainer("SupervisedTrainer")
    generator.job_config.with_aggregator(AggregatorStrategy.FED_AVG)
    # generator.job_config.with_aggregator("FedAvgAggregator")
    generator.train_config.with_model(fl_model.model)
    generator.train_config.with_optimizer(fl_model.MnistOptimizer, lr=0.2)
    generator.train_config.with_loss(fl_model.CrossEntropyLoss)
    generator.train_config.with_epoch(1)
    generator.aggregate_config.with_round(2)
    generator.aggregate_config.with_loss(fl_model.CrossEntropyLoss)
    job = generator.generate()
    JobManager.init_job_sqlite(job.job_id)
    JobManager.submit_job(job)
    print(job.job_id)
    return job


def generate_topology(job_id):
    # 生成3个node。1个是聚合方，2个是训练方
    node1 = GflNode.standalone_nodes[0]
    node2 = GflNode.standalone_nodes[1]
    node3 = GflNode.standalone_nodes[2]
    # 拓扑结构
    topology_config = TopologyConfig()
    topology_config.with_train_node_num(2)
    topology_config.with_server_nodes([node1.address])
    topology_config.with_client_nodes([node2.address, node3.address])
    topology_config.with_index2node([node1.address, node2.address, node3.address])
    tpmgr = CentralizedTopologyManager(topology_config)
    # tpmgr.add_server(server_node=node1, add_into_topology=True)
    # 加到拓扑结构当中
    # tpmgr.add_node_into_topology(node2)
    # tpmgr.add_node_into_topology(node3)
    # 生成中心化的拓扑结构
    tpmgr.generate_topology()
    save_topology_manager(job_id=job_id, topology_manager=tpmgr)
    return tpmgr


def generate_nodes():
    GflNode.init_node()
    GflNode.add_standalone_node()
    GflNode.add_standalone_node()
    GflNode.add_standalone_node()


if __name__ == "__main__":
    # generate_dataset()
    generate_nodes()
    job = generate_job()
    generate_topology(job.job_id)
