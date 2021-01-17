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

