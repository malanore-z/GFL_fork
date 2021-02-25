from typing import NoReturn

from gfl.net.abstract import NetSend, File


class StandaloneSend(NetSend):

    @classmethod
    def send_partial_params(cls, client: str, job_id: str, step: int, params: File) -> NoReturn:
        pass

    @classmethod
    def send_cmd_register(cls, job_id: str, client: str):
        pass
