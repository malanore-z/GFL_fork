import threading


__register_record = {}
__register_lock = threading.Lock()


def set_register_record(job_id, address, pub_key, dataset_id):
    global __register_record
    __register_lock.acquire()
    client_list = __register_record.get(job_id)
    if client_list is None:
        client_list = []
        __register_record[job_id] = client_list
    client_list.append({
        "address": address,
        "pub_key": pub_key,
        "dataset_id": dataset_id
    })
    __register_lock.release()


def get_register_record(job_id):
    __register_lock.acquire()
    client_list = __register_record.get(job_id, None)
    if client_list:
        client = client_list.pop(0)
    else:
        client = None
    __register_lock.release()
    return client
