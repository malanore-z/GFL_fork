from typing import Dict, Any

from gfl.utils import ModuleUtils
from gfl.utils.po_utils import PlainObject


class ConfigObject(PlainObject):

    name: str
    is_instance: bool = False
    is_builtin: bool = False
    args: Dict[str, Any]

    def __init__(self, **kwargs):
        super(ConfigObject, self).__init__(**kwargs)

    @classmethod
    def new_object(cls, *, module=None, obj=None, strategy=None, is_instance=None, **kwargs):
        if strategy is not None:
            name = strategy.value
            if is_instance is None:
                is_instance = False
            is_builtin = True
        else:
            name = ModuleUtils.get_name(module, obj)
            if name is None:
                raise ValueError("")
            if is_instance is None:
                is_instance = not (type(obj) == type)
            is_builtin = False
        args = kwargs.copy()
        return ConfigObject(name=name, is_instance=is_instance, is_builtin=is_builtin, args=args)
