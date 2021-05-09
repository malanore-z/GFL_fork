import os
from typing import NoReturn

import torch

from gfl.core.lfs.path import JobPath
from gfl.net.abstract import NetSend, File
from gfl.net.standlone.cache import set_register_record
from gfl.utils import PathUtils


class StandaloneSend(NetSend):

    @classmethod
    def send_partial_params(cls, client: str, job_id: str, step: int, params) -> NoReturn:
        # 这里的参数client，暂时认为是client_address
        # 在standalone模式下，trainer当前训练轮次得到的模型保存在指定路径下
        client_params_dir = JobPath(job_id).client_params_dir(step, client)
        os.makedirs(client_params_dir, exist_ok=True)
        # 保存 job_id.pth为文件名
        path = PathUtils.join(client_params_dir, job_id + '.pth')
        # path = client_params_dir + 'job_id.pth'
        torch.save(params, path)
        print("训练完成，已将模型保存至：" + str(client_params_dir))

    @classmethod
    def send_cmd_register(cls, job_id: str, address: str, pub_key: str, dataset_id: str):
        set_register_record(job_id, address, pub_key, dataset_id)
