__all__ = [
    "load_dataset",
    "save_dataset",
    "load_dataset_zip",
    "save_dataset_zip",
    "load_job",
    "save_job",
    "load_job_zip",
    "save_job_zip"
]

import json
from io import BytesIO

from gfl.conf import GflConf
from gfl.core.data import *
from gfl.core.data.config import *
from gfl.core.lfs.ipfs import Ipfs
from gfl.core.lfs.path import JobPath, DatasetPath
from gfl.core.lfs.types import File
from gfl.utils import ModuleUtils, PathUtils, ZipUtils


def __load_json(file_path, clazz):
    if PathUtils.exists(file_path):
        return None
    with open(file_path, "r") as f:
        d = json.loads(f.read())
    return clazz().from_dict(d)


def __save_json(file_path, obj):
    with open(file_path, "w") as f:
        f.write(json.dumps(obj.to_dict(), indent=4, ensure_ascii=False))


def load_dataset(dataset_id: str):
    """
    Load dataset from JSON file.

    :param dataset_id: dataset ID
    """
    dataset_path = DatasetPath(dataset_id)
    metadata = __load_json(dataset_path.metadata_file, DatasetMetadata)
    dataset_config = __load_json(dataset_path.dataset_config_file, DatasetConfig)
    return Dataset(dataset_id=dataset_id,
                   metadata=metadata,
                   dataset_config=dataset_config)


def save_dataset(dataset: Dataset, module):
    """
    Save dataset

    :param dataset: dataset to save
    :param module: dataset module
    """
    if module is None:
        module = dataset.dataset_config.module
    dataset_path = DatasetPath(dataset.dataset_id)
    dataset_path.makedirs()
    __save_json(dataset_path.metadata_file, dataset.metadata)
    __save_json(dataset_path.dataset_config_file, dataset.dataset_config)
    ModuleUtils.submit_module(module, dataset_path.module_name, dataset_path.config_dir)


def load_dataset_zip(dataset_id: str):
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
        return File(ipfs_hash=ipfs_hash)
    else:
        return File(file=file_obj)


def save_dataset_zip(dataset_id: str, dataset: File):
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


def load_job(job_id: str):
    """
    Load job from JSON file.

    :param job_id: dataset ID
    """
    job_path = JobPath(job_id)
    metadata = __load_json(job_path.metadata_file, JobMetadata)
    job_config = __load_json(job_path.job_config_file, JobConfig)
    train_config = __load_json(job_path.train_config_file, TrainConfig)
    aggregate_config = __load_json(job_path.aggregate_config_file, AggregateConfig)
    return Job(job_id=job_id,
               metadata=metadata,
               job_config=job_config,
               train_config=train_config,
               aggregate_config=aggregate_config)


def save_job(job: Job, module):
    """
    Save job

    :param job: job to save
    :param module: job module
    """
    if module is None:
        module = job.job_config.module
    job_path = JobPath(job.job_id)
    job_path.makedirs()
    __save_json(job_path.metadata_file, job.metadata)
    __save_json(job_path.job_config_file, job.job_config)
    __save_json(job_path.train_config_file, job.train_config)
    __save_json(job_path.aggregate_config_file, job.aggregate_config)
    ModuleUtils.submit_module(module, job_path.module_name, job_path.module_dir)


def load_job_zip(job_id: str):
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
        return File(ipfs_hash == ipfs_hash)
    else:
        return File(file=file_obj)


def save_job_zip(job_id: str, job: File):
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
