class Run:
    def __init__(
            self,
            info,
    ):
        self._info = info
    
    @property
    def info(self):
        return self._info
