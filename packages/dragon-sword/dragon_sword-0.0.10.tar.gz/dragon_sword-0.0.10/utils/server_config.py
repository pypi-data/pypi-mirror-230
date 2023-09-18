from utils.config import get_conf, get_default
from utils.data import Cache
from utils.file import make_dirs
from utils.system import get_host_ip


class _CommonConf(Cache):
    def __init__(self):
        super().__init__()
        self._name = "common"
        self._id: str
        self._flow_limit_path: str

    def _load(self):
        conf = get_conf(self._name)
        self._id = get_default(conf, "ID", get_host_ip())
        self._flow_limit_path = get_default(conf, "flow_limit_path", "flow_limit")
        make_dirs(self._flow_limit_path)

    @property
    def ID(self) -> str:
        return self.get("_id")

    @property
    def flow_limit_path(self) -> str:
        return self.get("_flow_limit_path")


CommonConf = _CommonConf()
