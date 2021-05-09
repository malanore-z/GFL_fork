
"""
create table kv (
    key text not null,
    value text
);
create unique index kv_key_uindex on kv (key);

create table client (
    address text not null,
    dataset text not null,
    pub_key text not null
);
create unique index client_address_uindex on client (address);

create table params (
    id integer not null
        constraint params_pk
            primary key autoincrement,
    step integer not null,
    is_global integer default 0 not null,
    node_address text not null,
    params text not null,
    params_check text not null
);
"""
create_job_kv = [
    "create table kv (key text not null, value text);",
    "create unique index kv_key_uindex on kv (key);"
]


create_job_client = [
    "create table client (address text not null, dataset text not null, pub_key text not null);",
    "create unique index client_address_uindex on client (address);"
]


create_job_params = [
    "create table params (id integer not null constraint params_pk primary key autoincrement,"
    "step integer not null, is_global integer default 0 not null, node_address text not null, "
    "params text not null, params_check text not null);"
]


insert_job_kv = "INSERT INTO kv(key, value) VALUES (?, ?)"
insert_job_client = "INSERT INTO client(address, dataset, pub_key) VALUES (?, ?, ?)"
insert_job_params = "INSERT INTO params(step, is_global, node_address, params, params_check) VALUES (?, ?, ?, ?, ?)"


select_job_kv_by_key = "SELECT key, value FROM kv WHERE key=?"
select_job_client_by_address = "SELECT address, dataset, pub_key FROM client WHERE address=?"
select_job_params_by_step_and_address = "SELECT id, step, is_global, node_address, params, params_check FROM params " \
                                        "WHERE step=? AND node_address=?"
select_client_by_job_id = "SELECT address, dataset, pub_key FROM client"
