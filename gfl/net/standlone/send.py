import pickle
import sys
from typing import NoReturn

from gfl.core.lfs.path import JobPath
from gfl.net.abstract import NetSend, File
from gfl.net.standlone.cache import set_register_record


class StandaloneSend(NetSend):

    @classmethod
    def send_partial_params(cls, client: str, job_id: str, step: int, params: File) -> NoReturn:
        pass

    @classmethod
    def send_cmd_register(cls, job_id: str, address: str, pub_key: str, dataset_id: str):
        set_register_record(job_id, address, pub_key, dataset_id)

    @classmethod
    def send(cls, client_address: str, job_id: str, step: int, name: str, data):
        client_dir = JobPath(job_id).client_params_dir(step, client_address)
        client_data_path = client_dir + f"/{name}.pkl"
        try:
            with open(client_data_path, 'wb') as pkl_file:
                pickled_data = pickle.dumps(data)
                data_size = sys.getsizeof(pickled_data)
                pickle.dump(pickled_data, pkl_file)
        except Exception as e:
            raise ValueError(f"数据 {data} 发送失败"
                             f"Error: {e}")
        return data_size
