import json
import os
import shutil
from pathlib import PurePath
from typing import Union

from gfl.conf import GflPath, GflNode
from gfl.core.config import *
from gfl.core.job import *
from gfl.utils import JobUtils, ModuleUtils


class Manager(object):

    @classmethod
    def _read_conf(cls, config: Union[Config, type], filepath):
        if not os.path.exists(filepath):
            return None
        if type(config) == type:
            config = config()
        with open(filepath, "r") as f:
            config.from_dict(json.loads(f.read()))
        return config

    @classmethod
    def _write_conf(cls, config: Config, filepath):
        with open(filepath, "w") as f:
            d = config.to_dict()
            f.write(json.dumps(d, indent=4))

    @classmethod
    def _list_uuid_subdir(cls, dir):
        ret = []
        for filename in os.listdir(dir):
            if not filename.startswith(".") and os.path.isdir(filename) and len(filename) == 32:
                ret.append(filename)
        return ret


class JobManager(Manager):

    def __init__(self):
        super(JobManager, self).__init__()

    @classmethod
    def generate_job(cls, module,
                     job_config: JobConfig = JobConfig(),
                     train_config: TrainConfig = TrainConfig(),
                     aggregate_config: AggregateConfig = AggregateConfig()) -> Job:
        """
        generate job
        :param module:
        :param job_config:
        :param train_config:
        :param aggregate_config:
        :return:
        """
        job_id = JobUtils.generate_job_id()
        if job_config.owner is None:
            job_config.owner = GflNode.address
        job = Job(job_id, job_config, train_config, aggregate_config)
        job_dir = PurePath(GflPath.job_dir, job_id).as_posix()
        os.makedirs(job_dir, exist_ok=True)
        ModuleUtils.submit_module(module, GflPath.model_module_name, job_dir)
        cls._write_conf(job_config, PurePath(job_dir, GflPath.job_conf_filename).as_posix())
        cls._write_conf(train_config, PurePath(job_dir, GflPath.train_conf_filename).as_posix())
        cls._write_conf(aggregate_config, PurePath(job_dir, GflPath.aggregate_conf_filename).as_posix())
        return job

    @classmethod
    def submit_job(cls, job_id):
        """
        Fake implement
        :param job_id:
        :return:
        """
        local_dir = PurePath(GflPath.job_dir, job_id).as_posix()
        remote_dir = PurePath(GflPath.server_dir, job_id).as_posix()
        shutil.copytree(local_dir, remote_dir)

    @classmethod
    def fetch_job(cls, job_id, dataset_id):
        """
        Fake implement
        :param job_id:
        :param dataset_id:
        :return:
        """
        remote_dir = PurePath(GflPath.server_dir, job_id).as_posix()
        local_dir = PurePath(GflPath.client_dir, job_id).as_posix()
        shutil.copytree(remote_dir, local_dir)
        dataset_conf_path = PurePath(GflPath.dataset_dir, dataset_id, GflPath.dataset_conf_filename).as_posix()
        shutil.copy(dataset_conf_path, PurePath(local_dir, GflPath.dataset_conf_filename))

    @classmethod
    def fetch_all_job(cls):
        cls.fetch_job("all")

    @classmethod
    def list_job_id(cls):
        return cls._list_uuid_subdir(GflPath.job_dir)

    @classmethod
    def list_server_job_id(cls):
        return cls._list_uuid_subdir(GflPath.server_dir)

    @classmethod
    def list_client_job_id(cls):
        return cls._list_uuid_subdir(GflPath.client_dir)

    @classmethod
    def load_job(cls, job_id):
        return cls.__load_job(job_id, GflPath.job_dir, Job)

    @classmethod
    def load_server_job(cls, job_id):
        return cls.__load_job(job_id, GflPath.server_dir, ServerJob)

    @classmethod
    def load_client_job(cls, job_id):
        return cls.__load_job(job_id, GflPath.client_dir, ClientJob)

    @classmethod
    def __load_job(cls, job_id, root_dir, job_type):
        job_path = PurePath(root_dir, job_id).as_posix()
        if not os.path.exists(job_path):
            return None
        job_config = cls._read_conf(JobConfig, PurePath(job_path, GflPath.job_conf_filename).as_posix())
        train_config = cls._read_conf(TrainConfig, PurePath(job_path, GflPath.train_conf_filename).as_posix())
        aggregate_config = cls._read_conf(AggregateConfig,
                                          PurePath(job_path, GflPath.aggregate_conf_filename).as_posix())
        dataset_config = cls._read_conf(DatasetConfig, PurePath(job_path, GflPath.dataset_conf_filename).as_posix())
        return job_type(job_id=job_id,
                        job_config=job_config,
                        train_config=train_config,
                        aggregate_config=aggregate_config,
                        dataset_config=dataset_config)


class DatasetManager(Manager):

    @classmethod
    def generate_dataset(cls, module,
                         dataset_config: DatasetConfig):
        dataset_id = JobUtils.generate_dataset_id()
        dataset_config.with_id(dataset_id)
        dataset_dir = PurePath(GflPath.dataset_dir, dataset_id).as_posix()
        os.makedirs(dataset_dir, exist_ok=True)
        ModuleUtils.submit_module(module, GflPath.dataset_module_name, dataset_dir)
        cls._write_conf(dataset_config, PurePath(dataset_dir, GflPath.dataset_conf_filename).as_posix())
        return dataset_id

    @classmethod
    def list_dataset_id(cls):
        return cls._list_uuid_subdir(GflPath.dataset_dir)

    @classmethod
    def load_dataset(cls, dataset_id):
        config_path = PurePath(GflPath.dataset_dir, dataset_id, GflPath.dataset_conf_filename).as_posix()
        return cls._read_conf(DatasetConfig, config_path)
