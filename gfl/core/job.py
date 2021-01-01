import json
import os
import sqlite3
import time
from pathlib import PurePath

from gfl.conf import GflPath
from gfl.core.config import TrainConfig, AggregateConfig, JobConfig, DatasetConfig


CREATE_KV_TABLE = """create table key_value (
    key text not null,
    value text
);"""

CREATE_CLIENT_TABLE = """create table client (
    address text not null,
    register_time integer not null
);"""

CREATE_PARAMS_TABLE = """create table params (
    client text not null,
    step integer not null,
    finish_time integer not null
);"""

CREATE_VALIDATION_TABLE = """create table validation (
    client text not null,
    step integer not null,
    correct integer not null,
    total integer not null,
    finish_time integer not null
);"""


class Job(object):

    def __init__(self, job_id: str,
                 job_config: JobConfig = None,
                 train_config: TrainConfig = None,
                 aggregate_config: AggregateConfig = None,
                 dataset_config: DatasetConfig = None):
        super(Job, self).__init__()
        self.job_id: str = job_id
        self.job_config = job_config
        self.train_config = train_config
        self.aggregate_config = aggregate_config
        self.dataset_config = dataset_config
        self.job_dir = PurePath(GflPath.job_dir, job_id).as_posix()

    def init_sqlite(self):
        db_path = PurePath(self.job_dir, GflPath.sqlite_db_filename).as_posix()
        if os.path.exists(db_path):
            os.remove(db_path)
        self.sqlite_conn = sqlite3.Connection(db_path)
        self._create_table(CREATE_KV_TABLE)

    def _load_sqlite(self):
        db_path = PurePath(self.job_dir, GflPath.sqlite_db_filename).as_posix()
        if os.path.exists(db_path):
            self.sqlite_conn = sqlite3.Connection(db_path)

    def update_kv(self, key, value):
        exists_key = self.get_key(key) is not None
        if exists_key:
            sql = "update key_value set value=? where key=?"
        else:
            sql = "insert into key_value(value, key) values (?, ?  )"
        cursor = self.sqlite_conn.cursor()
        cursor.execute(sql, (str(value), str(key)))
        cursor.close()
        self.sqlite_conn.commit()

    def get_key(self, key):
        cursor = self.sqlite_conn.cursor()
        select_sql = "select value from key_value where key=?"
        cursor.execute(select_sql, (key, ))
        values = cursor.fetchall()
        cursor.close()
        if len(values) == 1:
            return values[0][0]
        return None

    def _create_table(self, sql):
        cursor = self.sqlite_conn.cursor()
        cursor.execute(sql)
        cursor.close()
        self.sqlite_conn.commit()

    def _load_config(self):
        self.train_config = TrainConfig() if self.train_config is None else self.train_config
        self.aggregate_config = AggregateConfig() if self.aggregate_config is None else self.aggregate_config
        self.dataset_config = DatasetConfig() if self.dataset_config is None else self.dataset_config
        self.job_config = JobConfig() if self.job_config is None else self.job_config
        configs = {
            GflPath.train_conf_filename: self.train_config,
            GflPath.aggregate_conf_filename: self.aggregate_config,
            GflPath.dataset_conf_filename: self.dataset_config,
            GflPath.job_conf_filename: self.job_config
        }
        for k, v in configs.items():
            path = PurePath(self.job_dir, k).as_posix()
            if os.path.exists(path):
                with open(path, "r") as f:
                    data = json.loads(f.read())
                    v.from_dict(data)

    def __del__(self):
        if self.sqlite_conn is not None:
            self.sqlite_conn.close()


class ServerJob(Job):

    def __init__(self, job_id: str,
                 job_config: JobConfig = None,
                 train_config: TrainConfig = None,
                 aggregate_config: AggregateConfig = None,
                 dataset_config: DatasetConfig = None):
        super(ServerJob, self).__init__(job_id, job_config, train_config, aggregate_config, dataset_config)
        self.job_dir = PurePath(GflPath.server_dir, job_id).as_posix()
        self._load_config()
        self._load_sqlite()

    def init_sqlite(self):
        super(ServerJob, self).init_sqlite()
        self.__init_kv_table()
        self._create_table(CREATE_CLIENT_TABLE)
        self._create_table(CREATE_PARAMS_TABLE)
        self._create_table(CREATE_VALIDATION_TABLE)

    def __init_kv_table(self):
        self.update_kv("step", 0)
        self.update_kv("owner", self.job_config.owner)

    def current_step(self):
        step = self.get_key("step")
        if step is not None:
            return int(step)
        return 0

    def inc_step(self):
        step = self.current_step()
        self.update_kv("step", step + 1)

    def register_client(self, client):
        register_time = int(1000 * time.time())
        sql = "insert into client(address, register_time) values (?, ?)"
        cursor = self.sqlite_conn.cursor()
        cursor.execute(sql, (client, register_time))
        cursor.close()
        self.sqlite_conn.commit()

    def receive_params(self, client, step):
        finish_time = int(1000 * time.time())
        sql = "insert into params(client, step, finish_time) values (?, ?, ?)"
        cursor = self.sqlite_conn.cursor()
        cursor.execute(sql, (client, step, finish_time))
        cursor.close()
        self.sqlite_conn.commit()

    def receive_validation_result(self, client, step, result):
        finish_time = int(1000 * time.time())
        sql = "insert into validation(client, step, correct, total, finish_time) values (?, ?, ?, ? ,?)"
        cursor = self.sqlite_conn.cursor()
        cursor.execute(sql, (client, step, result[0], result[1], finish_time))
        cursor.close()
        self.sqlite_conn.commit()


class ClientJob(Job):

    def __init__(self, job_id: str,
                 job_config: JobConfig = None,
                 train_config: TrainConfig = None,
                 aggregate_config: AggregateConfig = None,
                 dataset_config: DatasetConfig = None):
        super(ClientJob, self).__init__(job_id, job_config, train_config, aggregate_config, dataset_config)
        self.job_dir = PurePath(GflPath.client_dir, job_id).as_posix()
