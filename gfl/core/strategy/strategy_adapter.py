

class StrategyAdapter(object):

    def get_type(self):
        return self._torch_type()

    def _torch_type(self):
        raise NotImplementedError("")
