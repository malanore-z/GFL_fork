import unittest
from gfl.utils.path_utils import *


class TestMethod(unittest.TestCase):

    # def setUp(self) -> None:
    #     print("do something before test")
    #
    # def tearDown(self) -> None:
    #     print("do something after test")

    def test(self):
        print(PathUtils.join('1', '2'+'3'))


if __name__ == '__main__':
    pass
