import importlib
import inspect
import os
import shutil
from pathlib import PurePath


class ModuleUtils(object):

    @classmethod
    def submit_module(cls, module, target_module_name, target_dir):
        cls.verify_module_api(module)
        module_path = inspect.getsourcefile(module)
        if module_path.endswith("__init__.py"):
            shutil.copytree(os.path.dirname(module_path), PurePath(target_dir, target_module_name).as_posix())
        else:
            shutil.copy(module_path, PurePath(target_dir, target_module_name + ".py").as_posix())

    @classmethod
    def import_module(cls, path, name=None):
        if name is not None:
            module_name = path.replace("/", ".") + "." + name
        else:
            module_name = path.replace("/", ".")
        return importlib.import_module(module_name)

    @classmethod
    def verify_module_api(cls, module):
        pass

    @classmethod
    def exists_module(cls, module):
        try:
            exec("import " + module)
            return True
        except:
            return False

    @classmethod
    def get_name(cls, module, obj):
        if module is None or obj is None:
            raise ValueError("")
        for k, v in module.__dict__.items():
            if v == obj:
                return k
        return None
