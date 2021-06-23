__all__ = [
    "load_dataset",
    "save_dataset",
    "load_dataset_zip",
    "save_dataset_zip",
    "load_job",
    "load_all_job",
    "save_job",
    "load_job_zip",
    "save_job_zip",
    "save_topology_manager",
    "load_topology_manager"
]

import json
import os
from io import BytesIO
from typing import NoReturn, List

from gfl.conf import GflConf
from gfl.core.data import *
from gfl.core.data.config import *
from gfl.core.lfs.ipfs import Ipfs
from gfl.core.lfs.path import JobPath, DatasetPath
from gfl.core.lfs.types import File
from gfl.topology.centralized_topology_manager import CentralizedTopologyManager
from gfl.utils import ModuleUtils, PathUtils, ZipUtils


def __load_json(file_path, clazz):
    if not PathUtils.exists(file_path):
        return None
    with open(file_path, "r") as f:
        d = json.loads(f.read())
    return clazz().from_dict(d)


def __save_json(file_path, obj):
    with open(file_path, "w") as f:
        f.write(json.dumps(obj.to_dict(), indent=4, ensure_ascii=False))


def load_dataset(dataset_id: str) -> Dataset:
    """
    Load dataset from JSON file.

    :param dataset_id: dataset ID
    """
    dataset_path = DatasetPath(dataset_id)
    metadata = __load_json(dataset_path.metadata_file, DatasetMetadata)
    dataset_config = __load_json(dataset_path.dataset_config_file, DatasetConfig)
    module = ModuleUtils.import_module(dataset_path.module_dir, dataset_path.module_name)
    dataset_config.module = module
    dataset = Dataset(dataset_id=dataset_id,
                      metadata=metadata,
                      dataset_config=dataset_config)
    dataset.module = module
    return dataset


def save_dataset(dataset: Dataset, module=None) -> NoReturn:
    """
    Save dataset

    :param dataset: dataset to save
    :param module: dataset module
    """
    if module is None:
        module = dataset.module
    dataset_path = DatasetPath(dataset.dataset_id)
    dataset_path.makedirs()
    __save_json(dataset_path.metadata_file, dataset.metadata)
    __save_json(dataset_path.dataset_config_file, dataset.dataset_config)
    ModuleUtils.submit_module(module, dataset_path.module_name, dataset_path.module_dir)


def load_dataset_zip(dataset_id: str) -> File:
    """
    Load dataset from a ZIP file.

    :param dataset_id: dataset ID
    """
    dataset_path = DatasetPath(dataset_id)
    file_obj = BytesIO()
    ZipUtils.compress(dataset_path.metadata_file, file_obj)
    if GflConf.get_property("ipfs.enabled"):
        file_obj.seek(0)
        ipfs_hash = Ipfs.put(file_obj.read())
        return File(ipfs_hash=ipfs_hash, file=None)
    else:
        return File(ipfs_hash=None, file=file_obj)


def save_dataset_zip(dataset_id: str, dataset: File) -> NoReturn:
    """
    Save the zip file of the dataset.

    :param dataset_id: dataset ID
    :param dataset: zip file
    """
    dataset_path = DatasetPath(dataset_id)
    if dataset.ipfs_hash is not None and dataset.ipfs_hash != "":
        file_obj = Ipfs.get(dataset.ipfs_hash)
    else:
        file_obj = dataset.file
    ZipUtils.extract(file_obj, dataset_path.root_dir)


def load_job(job_id: str) -> Job:
    """
    Load job from JSON file.

    :param job_id: dataset ID
    """
    job_path = JobPath(job_id)
    metadata = __load_json(job_path.metadata_file, JobMetadata)
    job_config = __load_json(job_path.job_config_file, JobConfig)
    train_config = __load_json(job_path.train_config_file, TrainConfig)
    aggregate_config = __load_json(job_path.aggregate_config_file, AggregateConfig)
    module = ModuleUtils.import_module(job_path.module_dir, job_path.module_name)
    job_config.module = module
    train_config.module = module
    aggregate_config.module = module
    job = Job(job_id=job_id,
              metadata=metadata,
              job_config=job_config,
              train_config=train_config,
              aggregate_config=aggregate_config)
    job.module = module
    return job


def load_all_job() -> List[Job]:
    job_dir = PathUtils.join(GflConf.data_dir, "job")
    jobs = []
    for filename in os.listdir(job_dir):
        path = PathUtils.join(job_dir, filename)
        if os.path.isdir(path):
            try:
                job = load_job(filename)
                jobs.append(job)
            except:
                pass
    return jobs


def save_job(job: Job, module=None) -> NoReturn:
    """
    Save job

    :param job: job to save
    :param module: job module
    """
    if module is None:
        module = job.module
    job_path = JobPath(job.job_id)
    job_path.makedirs()
    __save_json(job_path.metadata_file, job.metadata)
    __save_json(job_path.job_config_file, job.job_config)
    __save_json(job_path.train_config_file, job.train_config)
    __save_json(job_path.aggregate_config_file, job.aggregate_config)
    ModuleUtils.submit_module(module, job_path.module_name, job_path.module_dir)


def load_job_zip(job_id: str) -> File:
    """
    Load job from a ZIP file.

    :param job_id: dataset ID
    """
    job_path = JobPath(job_id)
    file_obj = BytesIO()
    ZipUtils.compress([job_path.metadata_file, job_path.config_dir], file_obj)
    if GflConf.get_property("ipfs.enabled"):
        file_obj.seek(0)
        ipfs_hash = Ipfs.put(file_obj.read())
        return File(ipfs_hash == ipfs_hash, file=None)
    else:
        return File(ipfs_hash=None, file=file_obj)


def save_job_zip(job_id: str, job: File) -> NoReturn:
    """
    Save the zip file of the job.

    :param job_id: job ID
    :param job: zip file
    """
    job_path = JobPath(job_id)
    if job.ipfs_hash is not None and job.ipfs_hash != "":
        file_obj = Ipfs.get(job.ipfs_hash)
    else:
        file_obj = File.file
    ZipUtils.extract(file_obj, job_path.root_dir)


def load_topology_manager(job_id: str):
    """
    Load topology_manager from JSON file.
    json->topology_config->topology_manager

    :param job_id: Job ID
    """
    job_path = JobPath(job_id)
    topology_config = __load_json(job_path.topology_config_file, TopologyConfig)
    if topology_config is not None and isinstance(topology_config, TopologyConfig):
        if topology_config.get_isCentralized() is True:
            topology_manager = CentralizedTopologyManager(topology_config=topology_config)
            return topology_manager


def save_topology_manager(job_id, topology_manager):
    """
    Save topology_manager
    topology_manager->topology_config->json

    :param job_id: Job ID
    :param topology_manager: topology_manager to save
    """
    job_path = JobPath(job_id)
    job_path.makedirs()
    topology_config = TopologyConfig()
    topology_config.with_topology(topology_manager.topology)
    topology_config.with_client_nodes(topology_manager.client_address_list)
    topology_config.with_index2node(topology_manager.server_address_list)
    topology_config.with_train_node_num(topology_manager.train_node_num)
    topology_config.with_server_nodes(topology_manager.server_address_list)
    # 目前暂时考虑中心化的场景
    topology_config.with_isCentralized(True)
    __save_json(job_path.topology_config_file, topology_config)
