from enum import Enum

from gfl.core.strategy import Strategy
from gfl.utils.po_utils import PlainObject


class ConfigObject(PlainObject):

    name = (str,)
    strategy = (str,)
    args = (dict, str)
    is_instance = (bool,)

    def __init__(self, obj=None, **kwargs):
        """

        :param obj: 可能为str， Stratege枚举， 类型
        :param kwargs:
        """
        super(ConfigObject, self).__init__()
        self.name, self.strategy = self.__get_name(obj)
        self.args = kwargs.copy()
        self.is_instance = type(obj) != type

    def __get_name(self, obj):
        if obj is None:
            # 特殊处理None
            return None, None
        else:
            if type(obj) == str:
                # 对于字符串类型的值， strategy设置为自定义
                return obj, Strategy.USER_DEFINED.value
            if isinstance(obj, Enum):
                # 对于Strategy枚举值， obj设置为None
                return None, obj.value
            return obj.__name__, Strategy.USER_DEFINED.value
