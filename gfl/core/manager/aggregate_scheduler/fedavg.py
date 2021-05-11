import abc
import time
from random import random

import base
from gfl.core.manager.job_status import JobStatus


class AggregateScheduler(base.AggregateScheduler):

    def __init__(self, *, node: GflNode, job, target_num):
        super(AggregateScheduler, self).__init__(node=node, job=job)
        self.trainer = None

        self.test_data = None
        self.selected_clients = None
        self.total_samples = 0

        self.clients_per_round = self.job.aggregate_config.clients_per_round
        self.start_time = 0

    def init_global_model(self):
        job_id = self.job.job_id
        path_util = JobPath(self.job.job_id)
        global_model_path = path_util.global_params_dir(0)
        os.makedirs(global_model_path, exist_ok=True)
        global_model_path += f"/{job_id}.pth"
        torch.save(self.job.train_config.get_model().state_dict(), global_model_path)

    def configure(self):
        """配置相关参数"""
        print(f"[Job {self.job.job_id} 初始化Aggregate Scheduler相关参数")
        total_rounds = self.job.aggregate_config.get_round()
        print(f"Training {total_rounds} rounds")

        # 加载对应的trainer
        self.load_trainer()

    def choose_clients(self):
        """选择部分client来参与模型的聚合"""
        assert (len(self.clients)) >= self.clients_per_round
        self.selected_clients = random.sample(list(self.clients),
                                              self.clients)
        self.start_time = time.time()

    def get_client_updates(self, reports):
        """从reports中获得client的权重更新值"""
        received_weights = [value for (_, value) in reports]
        return

    def load_trainer(self):
        self.job.job_config.trainer.is_instance = True
        trainer_clazz = self.job.job_config.get_trainer()
        self.trainer = trainer_clazz(job=self.job, step=self.step, client=self.node)

        # 测试数据的加载
