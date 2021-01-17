from gfl.utils import PathUtils


__home_dir = PathUtils.join(PathUtils.user_home_dir(), ".gfl")


def update_home_dir(dir):
    global __home_dir
    __home_dir = dir


def home_dir():
    global __home_dir
    return __home_dir


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
