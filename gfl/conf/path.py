import os
from pathlib import PurePath


class GflPath:

    gfl_dir = None
    tmp_dir = None
    logs_dir = None
    work_dir = None
    server_work_dir = None
    client_work_dir = None
    data_dir = None
    job_dir = None
    client_dir = None
    server_dir = None
    dataset_dir = None

    keyjson_filename = "key.json"
    conf_filename = "conf.yaml"
    train_conf_filename = "train.conf"
    aggregate_conf_filename = "aggregate.conf"
    job_conf_filename = "job.conf"
    dataset_conf_filename = "dataset.conf"
    sqlite_db_filename = "job.sqlite"
    model_module_name = "fl_model"
    dataset_module_name = "fl_dataset"


def update_root_dir(root_dir: str):
    if root_dir is None or len(root_dir.strip()) == 0:
        return
    GflPath.gfl_dir = PurePath(root_dir).as_posix()
    GflPath.tmp_dir = PurePath(GflPath.gfl_dir, "tmp").as_posix()
    GflPath.logs_dir = PurePath(GflPath.gfl_dir, "logs").as_posix()
    GflPath.work_dir = PurePath(GflPath.gfl_dir, "work").as_posix()
    GflPath.server_work_dir = PurePath(GflPath.work_dir, "server").as_posix()
    GflPath.client_work_dir = PurePath(GflPath.work_dir, "client").as_posix()
    GflPath.data_dir = PurePath(GflPath.gfl_dir, "data").as_posix()
    GflPath.job_dir = PurePath(GflPath.data_dir, "job").as_posix()
    GflPath.client_dir = PurePath(GflPath.data_dir, "client").as_posix()
    GflPath.server_dir = PurePath(GflPath.data_dir, "server").as_posix()
    GflPath.dataset_dir = PurePath(GflPath.data_dir, "dataset").as_posix()


update_root_dir(PurePath(os.path.expanduser("~"), ".gfl").as_posix())
