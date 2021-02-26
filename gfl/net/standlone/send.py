from typing import NoReturn

from gfl.net.abstract import NetSend, File
from gfl.net.standlone.cache import set_register_record


class StandaloneSend(NetSend):

    @classmethod
    def send_partial_params(cls, client: str, job_id: str, step: int, params: File) -> NoReturn:
        pass

    @classmethod
    def send_cmd_register(cls, job_id: str, address: str, pub_key: str, dataset_id: str):
        set_register_record(job_id, address, pub_key, dataset_id)
