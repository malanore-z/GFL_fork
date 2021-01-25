import json
import os
import shutil
from pathlib import PurePath
from typing import Union

from gfl.conf import GflPath
from gfl.core.config import *
from gfl.core.job import *
from gfl.utils import JobUtils, ModuleUtils


class Manager(object):
    """
    Manager is the parent class of JobManager and DatasetManager, which defines several common methods.
    """

    @classmethod
    def _read_conf(cls, config: Union[Config, type], filepath):
        """
        This method reads the serialized configuration parameters from the file at the specified path.

        parameters:
            config: the type of configuration that needs to be read
            filepath: the path of the file

        return:
            config: the parameter configuration instance read from the file
        """
        if not os.path.exists(filepath):
            return None
        if type(config) == type:
            config = config()
        with open(filepath, "r") as f:
            config.from_dict(json.loads(f.read()))
        return config

    @classmethod
    def _write_conf(cls, config: Config, filepath):
        """
        This method writes the serialized configuration parameters into the file at the specified path.

        parameters:
            config: the parameter configuration which needs to be written into the file
            filepath: the path of the file

        return:
            None
        """
        with open(filepath, "w") as f:
            d = config.to_dict()
            f.write(json.dumps(d, indent=4))

    @classmethod
    def _list_uuid_subdir(cls, dir):
        """
        This method lists all the subfolders under the folder that meet the UUID rule.

        parameters:
            dir: the path of the folder

        return:
            ret: all the subfolders that meet the UUID rule
        """
        ret = []
        for filename in os.listdir(dir):
            if not filename.startswith(".") and os.path.isdir(filename) and len(filename) == 32:
                ret.append(filename)
        return ret


class JobManager(Manager):
    """
    This class manages the generation, storage, transmission and state transition of the job.
    """

    def __init__(self):
        super(JobManager, self).__init__()

    @classmethod
    def generate_job(cls, module,
                     job_config: JobConfig = JobConfig(),
                     train_config: TrainConfig = TrainConfig(),
                     aggregate_config: AggregateConfig = AggregateConfig()) -> Job:
        """
        This method generate the job according to the given configuration parameters, and saved it to the local file
        system.

        parameters:
            module: Python module, which is necessary to generate a job. The package or source file
            corresponding to the module will be copied to the job directory.
            job_config: the configuration parameters of the job
            train_config: the configuration parameters of the training
            aggregate_config: the configuration parameters of the aggregating

        return:
            job: the generated job
        """
        job_id = JobUtils.generate_job_id()
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
        This method submits the generated job to the server. Then the server will take over the running process.

        parameters:
           job_id: the UUID of the job

        return:
            None

        """
        local_dir = PurePath(GflPath.job_dir, job_id).as_posix()
        remote_dir = PurePath(GflPath.server_dir, job_id).as_posix()
        shutil.copytree(local_dir, remote_dir)

    @classmethod
    def fetch_job(cls, job_id, dataset_id):
        """
        This method fetches the job details from the server and save in the local file.

        parameters:
            job_id: the UUID of the job
            dataset_id: the ID of the dataset

        return:
            None

        """
        remote_dir = PurePath(GflPath.server_dir, job_id).as_posix()
        local_dir = PurePath(GflPath.client_dir, job_id).as_posix()
        shutil.copytree(remote_dir, local_dir)
        dataset_conf_path = PurePath(GflPath.dataset_dir, dataset_id, GflPath.dataset_conf_filename).as_posix()
        shutil.copy(dataset_conf_path, PurePath(local_dir, GflPath.dataset_conf_filename))

    @classmethod
    def fetch_all_job(cls):
        """
        This method fetches all job details from the server.

        """
        cls.fetch_job("all")

    @classmethod
    def list_job_id(cls):
        """
        This method lists the UUIDs of all jobs generated in the local node.

        """
        return cls._list_uuid_subdir(GflPath.job_dir)

    @classmethod
    def list_server_job_id(cls):
        """
        This method lists the UUIDs of all jobs in the server node.

        """
        return cls._list_uuid_subdir(GflPath.server_dir)

    @classmethod
    def list_client_job_id(cls):
        """
        This method lists the UUIDs of all jobs participating in the training in the client node.

        """
        return cls._list_uuid_subdir(GflPath.client_dir)

    @classmethod
    def load_job(cls, job_id):
        """
        This method load the job generated by the local node according to the UUID.

        parameters:
            job_id: the UUID of the job

        return:
            Job: the job generated by the local node

        """
        return cls.__load_job(job_id, GflPath.job_dir, Job)

    @classmethod
    def load_server_job(cls, job_id):
        """
        This method load the job on the server which saved in the local cache according to the UUID.

        parameters:
            job_id: the UUID of the job

        return:
            ServerJob: the job on the remote server

        """
        return cls.__load_job(job_id, GflPath.server_dir, ServerJob)

    @classmethod
    def load_client_job(cls, job_id):
        """
        This method load the job in the local node which participates in the training according to the UUID.

        parameters:
            job_id: the UUID of the job

        return:
            ClientJob: the job in the local node which participates in the training

        """
        return cls.__load_job(job_id, GflPath.client_dir, ClientJob)

    @classmethod
    def __load_job(cls, job_id, root_dir, job_type):
        """
        This method load the job of the corresponding job_type according to the UUID and root directory.

        parameters:
            job_id: the UUID of the job
            root_dir: the root directory of the job
            job_type: the type of the job

        return:
            Job: the job of the corresponding job_type

        """
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
    """
    This class manages the generation and loading of the dataset.
    """

    @classmethod
    def generate_dataset(cls, module,
                         dataset_config: DatasetConfig):
        """
        The dataset configuration is generated and stored in the local file system according to the given
        configuration parameters.

        parameters:
            module: Python module, which is necessary to generate a dataset. The package or source file
            corresponding to the module will be copied to the dataset directory.
            dataset_config: the configuration parameters of the dataset

        return:
            dataset_id: the id of the generated dataset

        """
        dataset_id = JobUtils.generate_dataset_id()
        dataset_config.with_id(dataset_id)
        dataset_dir = PurePath(GflPath.dataset_dir, dataset_id).as_posix()
        os.makedirs(dataset_dir, exist_ok=True)
        ModuleUtils.submit_module(module, GflPath.dataset_module_name, dataset_dir)
        cls._write_conf(dataset_config, PurePath(dataset_dir, GflPath.dataset_conf_filename).as_posix())
        return dataset_id

    @classmethod
    def list_dataset_id(cls):
        """
        This method lists the UUIDs of all dataset generated in the local node.

        """
        return cls._list_uuid_subdir(GflPath.dataset_dir)

    @classmethod
    def load_dataset(cls, dataset_id):
        """
        This method loads the dataset in the local node according to the dataset_id.

        parameters:
            dataset_id: the id of the dataset

        """
        config_path = PurePath(GflPath.dataset_dir, dataset_id, GflPath.dataset_conf_filename).as_posix()
        return cls._read_conf(DatasetConfig, config_path)
