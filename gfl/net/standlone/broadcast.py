from typing import NoReturn

from gfl.net.abstract import NetBroadcast, File


class StandaloneBroadcast(NetBroadcast):

    @classmethod
    def broadcast_job(cls, job_id: str, job: File) -> NoReturn:
        # Nothing to do
        pass

    @classmethod
    def broadcast_dataset(cls, dataset_id: str, dataset: File) -> NoReturn:
        # Nothing to do
        pass

    @classmethod
    def broadcast_global_params(cls, job_id: str, step: int, params: File) -> NoReturn:
        pass
