import os
from typing import Tuple

from gfl.core.lfs.path import JobPath
from gfl.net.abstract import NetReceive, File
from gfl.net.standlone.cache import get_register_record
from gfl.utils import PathUtils


class StandaloneReceive(NetReceive):

    @classmethod
    def receive_job(cls) -> Tuple:
        pass

    @classmethod
    def receive_partial_params(cls, client: str, job_id: str, step: int) -> File:
        pass

    @classmethod
    def receive_global_params(cls, job_id: str, cur_round: int):
        # 在standalone模式下，trainer获取当前聚合轮次下的全局模型
        # 根据 Job 中的 job_id 和 cur_round 获取指定轮次聚合后的 全局模型参数的路径
        global_params_dir = JobPath(job_id).global_params_dir(cur_round)
        model_params_path = PathUtils.join(global_params_dir, job_id + '.pth')
        # 判断是否存在模型参数文件，如果存在则返回。
        if os.path.exists(global_params_dir) and os.path.isfile(model_params_path):
            # resources_already:1
            # self.__status = JobStatus.RESOURCE_ALREADY
            print("训练方接收全局模型")
            return model_params_path
        else:
            # 等待一段时间。在这段时间内获取到了模型参数文件，则返回
            # 暂时不考虑这种情况
            # 否则，认为当前模型参数文件已经无法获取
            return None

    @classmethod
    def receive_cmd_register(cls, job_id: str):
        return get_register_record(job_id)
