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
    def import_module(cls, path, name):
        module_name = path.replace("/", ".") + "." + name
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