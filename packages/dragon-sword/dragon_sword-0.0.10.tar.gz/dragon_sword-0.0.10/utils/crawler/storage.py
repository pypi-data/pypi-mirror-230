from utils.file import (
    f_other_format
)
from utils.mq.file import FileMQ
from utils.storage.download import FileStorage


class _Storage(FileMQ, FileStorage):
    def __init__(self, site, s_dir: str, record_dir: str = "records"):
        FileMQ.__init__(self, site, record_dir)

        FileStorage.__init__(self, site, s_dir)

    @staticmethod
    def _video_suffix():
        return ["ts", "mp4"]

    def exist_video(self, name: str) -> bool:
        for _format in self._video_suffix():
            name = f_other_format(name, _format)
            if self.exist_f(name):
                return True
        return False

    def rename(self, ori_name, name):
        suffix = [""]
        suffix.extend(self._video_suffix())
        return self.rename_with_suffix(ori_name, name, suffix)
