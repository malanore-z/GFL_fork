

class ManagerHolder(object):

    default_manager = None
    standalone_managers = []

    @classmethod
    def get_manager(cls):
        return cls.default_manager

    @classmethod
    def get_standalone_manager(cls, idx: int):
        if idx < len(cls.standalone_managers):
            return cls.standalone_managers[idx]
        return None
