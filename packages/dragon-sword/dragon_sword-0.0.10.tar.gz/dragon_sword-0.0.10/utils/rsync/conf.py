from utils.data import Cache
from utils.config import get_conf, get_default
from utils.file import get_file_path
from utils.system import is_win


class _Conf(Cache):
    def __init__(self):
        super().__init__()
        self._name = "rsync"
        self._path: str
        self._rsync_bin: str
        self._ssh_bin: str

    def _load(self):
        conf = get_conf(self._name)
        default_p = ""
        if is_win():
            default_p = r'"C:\Program Files\cwRsync"'
        self._path = get_default(conf, "path", default_p)

        self._rsync_bin = get_file_path(self._path, "rsync")
        self._ssh_bin = get_file_path(self._path, "ssh")

        if is_win():
            self._rsync_bin = f"{self._rsync_bin}.exe"
            self._ssh_bin = f"{self._ssh_bin}.exe"

    @property
    def rsync_bin(self):
        return self.get("_rsync_bin")

    @property
    def ssh_bin(self):
        return self.get("_ssh_bin")


Conf = _Conf()
