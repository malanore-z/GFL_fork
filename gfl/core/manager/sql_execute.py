__all__ = [
    "KVEntity",
    "ClientEntity",
    "ParamsEntity",
    "create_tables",
    "get_kv",
    "get_client",
    "get_params",
    "save_kv",
    "save_client",
    "save_params",
    "get_client_by_job_id",
    "update_kv"
]

import os
from collections import namedtuple

from gfl.core.context import SqliteContext
from gfl.core.lfs.path import JobPath
from gfl.core.manager.sql_statement import *


KVEntity = namedtuple("KVEntity", ["key", "value"], defaults=[None, None])
ClientEntity = namedtuple("ClientEntity", ["address", "dataset", "pub_key"], defaults=[None, None, None])
ParamsEntity = namedtuple("ParamsEntity", ["id", "step", "is_global", "node_address", "params", "params_check"], defaults=[None, None, None, None, None, None])


"""
insert_job_kv = "INSERT INTO kv(key, value) VALUES (?, ?)"
insert_job_client = "INSERT INTO client(address, dataset, pub_key) VALUES (?, ?, ?)"
insert_job_params = "INSERT INTO params(step, is_global, node_address, params, params_check) VALUES (?, ?, ?, ?, ?)"


select_job_kv_by_key = "SELECT * FROM kv WHERE key=?"
select_job_client_by_address = "SELECT * FROM client WHERE address=?"
select_job_params_by_step_and_address = "SELECT * FROM params WHERE step=? AND node_address=?"
"""


def create_tables(job_id: str):
    job_path = JobPath(job_id)
    job_path.makedirs()
    with SqliteContext(job_path.sqlite_file) as (_, cursor):
        for s in create_job_kv:
            cursor.execute(s)
        for s in create_job_client:
            cursor.execute(s)
        for s in create_job_params:
            cursor.execute(s)


def save_kv(job_id: str, kv: KVEntity):
    __save(job_id, insert_job_kv, kv.key, kv.value)


def update_kv(job_id: str, kv: KVEntity):
    __save(job_id, update_job_kv, kv.value, kv.key)


def get_kv(job_id: str, key: str):
    entities = __get(job_id, select_job_kv_by_key, key)
    ret = []
    for e in entities:
        ret.append(KVEntity(key=e[0], value=e[1]))
    return ret


def save_client(job_id: str, client: ClientEntity):
    __save(job_id, insert_job_client, client.address, client.dataset, client.pub_key)


def get_client_by_job_id(job_id: str):
    entities = __get(job_id, select_client_by_job_id)
    ret = []
    for e in entities:
        ret.append(ClientEntity(address=e[0], dataset=e[1], pub_key=e[2]))
    return ret


def get_client(job_id: str, address: str):
    entities = __get(job_id, select_job_client_by_address, address)
    ret = []
    for e in entities:
        ret.append(ClientEntity(address=e[0], dataset=e[1], pub_key=e[2]))
    return ret


def save_params(job_id: str, params: ParamsEntity):
    __save(job_id, insert_job_params,
           params.step, params.is_global, params.node_address, params.params, params.params_check)


def get_params(job_id: str, step: int, address: str):
    entities = __get(job_id, select_job_params_by_step_and_address, step, address)
    ret = []
    for e in entities:
        ret.append(ParamsEntity(id=e[0], step=e[1], is_global=e[2], node_address=e[3], params=e[4], params_check=e[5]))
    return ret


def __save(job_id: str, statement: str, *params):
    job_path = JobPath(job_id)
    with SqliteContext(job_path.sqlite_file) as (_, cursor):
        cursor.execute(statement, tuple(params))


def __get(job_id: str, statement: str, *params):
    job_path = JobPath(job_id)
    with SqliteContext(job_path.sqlite_file) as (_, cursor):
        cursor.execute(statement, tuple(params))
        ret = cursor.fetchall()
    return ret