import gfl_test
from gfl.conf.node import GflNode
from gfl.core.lfs.data import save_topology_manager

from gfl.core.manager import JobManager, DatasetManager
from gfl.core.manager.generator import DatasetGenerator, JobGenerator
from gfl.core.strategy import *

import gfl_test.model as fl_model
import gfl_test.dataset as fl_dataset
from gfl.topology.centralized_topology_manager import CentralizedTopologyManager


def generate_dataset():
    generator = DatasetGenerator(fl_dataset)
    generator.metadata.content = "mnist dataset"
    generator.dataset_config.with_dataset(fl_dataset.mnist_dataset)
    generator.dataset_config.with_val_rate(0.2)
    dataset = generator.generate()
    DatasetManager.submit_dataset(dataset)
    # print(dataset.dataset_id)
    return dataset


def generate_job():
    generator = JobGenerator(fl_model)
    generator.metadata.content = "mnist CNN"
    generator.job_config.with_trainer(TrainerStrategy.SUPERVISED)
    generator.job_config.with_aggregator(AggregatorStrategy.FED_AVG)
    generator.train_config.with_model(fl_model.model)
    generator.train_config.with_optimizer(fl_model.MnistOptimizer, lr=0.2)
    generator.train_config.with_loss(fl_model.CrossEntropyLoss)
    generator.train_config.with_epoch(2)
    generator.aggregate_config.with_round(2)
    job = generator.generate()
    JobManager.init_job_sqlite(job.job_id)
    JobManager.submit_job(job)
    # print(job.job_id)
    return job


def generate_topology(job_id):
    # 生成3个node。1个是聚合方，2个是训练方
    GflNode.init_node()
    node1 = GflNode.default_node
    GflNode.init_node()
    node2 = GflNode.default_node
    GflNode.init_node()
    node3 = GflNode.default_node
    # 拓扑结构
    tpmgr = CentralizedTopologyManager(train_node_num=2, job_id=job_id)
    tpmgr.add_server(server_node=node1, add_into_topology=True)
    # 加到拓扑结构当中
    tpmgr.add_node_into_topology(node2)
    tpmgr.add_node_into_topology(node3)
    # 生成中心化的拓扑结构
    tpmgr.generate_topology()
    save_topology_manager(job_id=job_id, topology_manager=tpmgr)
    return tpmgr


if __name__ == "__main__":
    generate_dataset()
    job = generate_job()
    generate_topology(job.job_id)
