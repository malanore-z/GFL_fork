from typing import Tuple

from gfl.net.abstract import NetReceive, File


class StandaloneReceive(NetReceive):

    @classmethod
    def receive_job(cls) -> Tuple:
        pass

    @classmethod
    def receive_partial_params(cls, client: str, job_id: str, step: int) -> File:
        pass

    @classmethod
    def receive_cmd_register(cls, job_id: str):
        pass
