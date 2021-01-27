__all__ = [
    "load_job",
    "save_job",
    "load_dataset",
    "save_dataset"
]

import json
import os

import gfl.core.lfs.path as lfs_path
from gfl.core.config import *
from gfl.core.data import *
from gfl.utils import PathUtils, ModuleUtils


def __load_json(file_path, cls):
    if PathUtils.exists(file_path):
        return None
    with open(file_path, "r") as f:
        d = json.loads(f.read())
    return cls().from_dict(d)


def __save_json(file_path, obj):
    with open(file_path, "w") as f:
        f.write(json.dumps(obj.to_dict(), indent=4, ensure_ascii=False))


def load_job(job_id):
    job_path = lfs_path.job_dir(job_id)
    metadata = __load_json(PathUtils.join(job_path, lfs_path.metadata_filename), JobMetadata)
    config_path = PathUtils.join(job_path, "job")
    job_config = __load_json(PathUtils.join(config_path, lfs_path.job_config_filename), JobConfig)
    train_config = __load_json(PathUtils.join(config_path, lfs_path.train_config_filename), TrainConfig)
    aggregate_config = __load_json(PathUtils.join(config_path, lfs_path.aggregate_config_filename), AggregateConfig)
    return Job(job_id=job_id,
               metadata=metadata,
               job_config=job_config,
               train_config=train_config,
               aggregate_config=aggregate_config)


def save_job(job: Job, module):
    job_path = lfs_path.job_dir(job.job_id)
    config_path = PathUtils.join(job_path, "job")
    os.makedirs(config_path, exist_ok=True)
    __save_json(PathUtils.join(job_path, lfs_path.metadata_filename), job.metadata)
    __save_json(PathUtils.join(config_path, lfs_path.job_config_filename), job.job_config)
    __save_json(PathUtils.join(config_path, lfs_path.train_config_filename), job.train_config)
    __save_json(PathUtils.join(config_path, lfs_path.aggregate_config_filename), job.aggregate_config)
    ModuleUtils.submit_module(module, lfs_path.model_module_name, config_path)


def load_dataset(dataset_id):
    dataset_path = lfs_path.dataset_dir(dataset_id)
    metadata = __load_json(PathUtils.join(dataset_path, lfs_path.metadata_filename), DatasetMetadata)
    config_path = PathUtils.join(dataset_path, "dataset")
    dataset_config = __load_json(PathUtils.join(config_path, lfs_path.dataset_config_filename), DatasetConfig)
    return Dataset(dataset_id=dataset_id,
                   metadata=metadata,
                   dataset_config=dataset_config)


def save_dataset(dataset: Dataset, module):
    dataset_path = lfs_path.dataset_dir(dataset.dataset_id)
    config_path = PathUtils.join(dataset_path, "dataset")
    os.makedirs(config_path, exist_ok=True)
    __save_json(PathUtils.join(dataset_path, lfs_path.metadata_filename), dataset.metadata)
    __save_json(PathUtils.join(config_path, lfs_path.dataset_config_filename), dataset.dataset_config)
    ModuleUtils.submit_module(module, lfs_path.dataset_module_name, config_path)
