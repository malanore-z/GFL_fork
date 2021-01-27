import gfl
from gfl.utils import PathUtils


train_config_filename = "train.json"
aggregate_config_filename = "aggregate.json"
dataset_config_filename = "dataset.json"
job_config_filename = "job.json"
metadata_filename = "metadata.json"
model_module_name = "fl_model"
dataset_module_name = "fl_dataset"


__home_dir = PathUtils.join(PathUtils.user_home_dir(), ".gfl")


def update_home_dir(dir):
    gfl.home_dir = dir


def home_dir():
    return gfl.home_dir


def cache_dir():
    return PathUtils.join(home_dir(), "cache")


def data_dir():
    return PathUtils.join(home_dir(), "data")


def job_dir(job_id: str):
    return PathUtils.join(data_dir(), "job", job_id)


def dataset_dir(dataset_id: str):
    return PathUtils.join(data_dir(), "dataset", dataset_id)


def client_dir():
    return PathUtils.join(data_dir(), "client")


def client_job_dir(job_id):
    return PathUtils.join(client_dir(), job_id)


def server_dir():
    return PathUtils.join(data_dir(), "server")


def server_job_dir(job_id):
    return PathUtils.join(server_dir(), job_id)
