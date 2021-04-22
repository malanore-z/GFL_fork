import unittest
from gfl.net.http.http import *


class TestMethod(unittest.TestCase):

    # def setUp(self) -> None:
    #     print("do something before test")
    #
    # def tearDown(self) -> None:
    #     print("do something after test")

    def test_GflConf(self):
        Http.concat_url('123', None)


if __name__ == '__main__':
    pass
