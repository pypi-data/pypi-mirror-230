from svn.local import LocalClient
from svn.constants import ST_CONFLICTED
from svn.exception import SvnException
from utils.log import logger
from utils.data import CacheKey


class _SvnCli(CacheKey):
    def _load(self, key: str) -> LocalClient:
        return LocalClient(key)

    def _update_proj(self, work_dir: str):
        cli: LocalClient = self.get(work_dir)
        try:
            cli.update([work_dir])
        except SvnException:
            return False
        return True

    def update_proj(self, work_dir: str) -> str:
        if not self._update_proj(work_dir):
            cli: LocalClient = self.get(work_dir)
            try:
                cli.cleanup()
            except SvnException as e:
                logger.error(f"update_proj {work_dir} err={e}")
                return f"{e}"
            else:
                if not self._update_proj(work_dir):
                    logger.info(f"update_proj {work_dir} fail")
                    return f"update fail"
        logger.info(f"update_proj {work_dir} success")
        return ""

    def get_conflict_dir(self, work_dir: str) -> list[str]:
        cli: LocalClient = self.get(work_dir)
        # 冲突文件
        _dirs = []
        for change in cli.status():
            if change.type == ST_CONFLICTED:
                _dirs.append(change.name)
        return _dirs


SvnCli = _SvnCli()
