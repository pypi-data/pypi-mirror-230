class Run:
    def __init__(
            self,
            info,
            name=None,
    ):
        self._info = info
        self._name = name
    
    @property
    def info(self):
        return self._info

    @property
    def name(self):
        return self._name
