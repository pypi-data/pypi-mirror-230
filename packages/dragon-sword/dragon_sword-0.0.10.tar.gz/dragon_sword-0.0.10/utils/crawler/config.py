from utils.data import Cache
from utils.config import get_conf, get_default


class _Conf(Cache):
    def __init__(self):
        super().__init__()
        self._name = "crawler"
        self._headless: bool
        self._timeout: int

    def _load(self):
        conf = get_conf(self._name)
        self._headless = get_default(conf, "headless", True)
        self._timeout = get_default(conf, "timeout", 60 * 60)

    @property
    def headless(self):
        return self.get("_headless")

    @property
    def timeout(self):
        return self.get("_timeout")


Conf = _Conf()
