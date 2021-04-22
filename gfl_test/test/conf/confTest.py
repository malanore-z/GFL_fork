import unittest
import os

from gfl.conf.conf import *
from gfl.conf.node import *
from gfl.core.lfs.path import *

import gfl.net


class TestMethod(unittest.TestCase):

    # def setUp(self) -> None:
    #     print("do something before test")
    #
    # def tearDown(self) -> None:
    #     print("do something after test")

    def test_GflConf(self):
        # key_dir = PathUtils.join(GflConf.home_dir, "key")
        # print(key_dir)
        # key_file = PathUtils.join(key_dir, "key.json")
        # print(key_file)
        # GflNode.init_node()
        # GflNode.add_standalone_node()
        # default_node = None
        # standalone_nodes = {}
        # GflNode.load_node()
        # print(GflNode.default_node)
        # print(GflNode.standalone_nodes)
        # print(GflNode.standalone_nodes)
        # readonly_props = {}
        #
        # home_dir = PathUtils.join(PathUtils.user_home_dir(),".gfl")
        # data_dir = PathUtils.join(home_dir, "data")
        #
        # with open(PathUtils.join(home_dir, "conf.yaml"), "r") as f:  # /Users/YY/.gfl/conf.yaml
        #     yaml.safe_dump(default_conf, f)

        # print(readonly_props)

        # GflConf.props = {}
        # GflConf.readonly_props = {}
        # GflConf.reload()
        # job_round = self.job.round
        job_id = '1'
        job_round = 2
        print(JobPath(job_id).global_params_dir(job_round))


if __name__ == '__main__':
    unittest.main()
